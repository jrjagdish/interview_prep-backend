import asyncio
import os
import json
from typing import AsyncIterator
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, Depends
from fastapi.middleware.cors import CORSMiddleware
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from sqlalchemy.orm import Session

# Local Imports
from app.ai.assemblyai_stt import AssemblyAISTT
from app.ai.tts_cartesia import CartesiaTTS
from app.utils.events import (
    STTOutputEvent,
    AgentChunkEvent,
    AgentEndEvent,
    event_to_dict,
)
from app.routes import auth, adminroutes, guest, interviewroute
from app.db.session import get_db
from app.models.interview import InterviewQA, InterviewSession

load_dotenv()

app = FastAPI(title="Interview Preparation App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. THE BRAIN (LLM)
llm = ChatGroq(model="llama-3.3-70b-versatile", streaming=True)


async def interview_brain(transcript: str, chat_history: list) -> AsyncIterator:
    """Processes text and yields streaming agent chunks."""
    system_prompt = (
        "You are a friendly technical interviewer. "
        "Be extremely concise (1-2 sentences maximum per response). "
        "Stop talking immediately after delivering the main point or question. "
        "Do not offer filler text. Prioritize getting back to the user quickly."
    )

    # Build messages with history
    messages = [SystemMessage(content=system_prompt)]
    for turn in chat_history:
        messages.append(HumanMessage(content=turn["user"]))
        messages.append(SystemMessage(content=turn["ai"]))
    messages.append(HumanMessage(content=transcript))

    async for chunk in llm.astream(messages):
        yield AgentChunkEvent.create(chunk.content)
    yield AgentEndEvent.create()


async def run_pipeline(audio_stream: AsyncIterator[bytes], websocket: WebSocket, session_id: str, db: Session):
    """
    Handles the end-to-end voice pipeline:
    STT (AssemblyAI) -> LLM (Groq) -> TTS (Cartesia) + Database Persistence.
    """
    # Initialize services
    stt = AssemblyAISTT(sample_rate=16000)
    tts = CartesiaTTS()

    # TASK A: Listen to the Microphone and send to AssemblyAI
    async def stt_sender():
        try:
            async for chunk in audio_stream:
                await stt.send_audio(chunk)
        except Exception as e:
            print(f"Error in stt_sender: {e}")
        finally:
            await stt.close()

    # TASK B: Listen for synthesized audio from Cartesia and send to Browser
    async def tts_receiver():
        try:
            async for tts_event in tts.receive_events():
                await websocket.send_json(event_to_dict(tts_event))
        except Exception as e:
            print(f"Error in tts_receiver: {e}")

    # Fire off background tasks
    stt_task = asyncio.create_task(stt_sender())
    tts_task = asyncio.create_task(tts_receiver())

    # --- DATABASE LOAD/INITIALIZE ---
    session_obj = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session_obj:
        print(f"Session {session_id} not found")
        return
    
    qa_record = db.query(InterviewQA).filter(InterviewQA.session_id == session_id).first()
    if not qa_record:
        # Initialize with default values to satisfy NotNullViolation
        qa_record = InterviewQA(
            session_id=session_id, 
            chat_history=[],
            question_index=0 
        )
        db.add(qa_record)
        db.commit()

    # --- FIX: Ensure chat_history is a Python LIST, not a DICT ---
    history_raw = qa_record.chat_history
    
    if isinstance(history_raw, str):
        chat_history = json.loads(history_raw)
    else:
        chat_history = history_raw
    
    # If the database stored a dict {}, or was None, make it a list []
    if not isinstance(chat_history, list):
        chat_history = []

    # MAIN LOOP: Process Transcripts -> LLM -> TTS Trigger
    try:
        async for stt_event in stt.receive_events():
            # Send partial transcripts to frontend for real-time display
            await websocket.send_json(event_to_dict(stt_event))

            # STTOutputEvent means the speaker paused and AssemblyAI finalized the sentence
            if isinstance(stt_event, STTOutputEvent):
                transcript = stt_event.transcript
                print(f"DEBUG: Processing Finalized Transcript: {transcript}")
                
                # --- LLM Processing ---
                text_buffer = []
                async for agent_event in interview_brain(transcript, chat_history):
                    await websocket.send_json(event_to_dict(agent_event))
                    
                    if isinstance(agent_event, AgentChunkEvent):
                        text_buffer.append(agent_event.text)
                    
                    if isinstance(agent_event, AgentEndEvent):
                        ai_response = "".join(text_buffer)
                        # Trigger TTS
                        await tts.send_text(ai_response)
                        
                        # --- UPDATE CHAT HISTORY ---
                        # Now chat_history is guaranteed to be a list
                        chat_history.append({"user": transcript, "ai": ai_response})
                        
                        # Serialize list back to JSON string for DB
                        qa_record.chat_history = json.dumps(chat_history)
                        db.commit()
    except Exception as e:
        print(f"Error in main loop: {e}")
    finally:
        # Clean up tasks
        stt_task.cancel()
        tts_task.cancel()
        await tts.close()


@app.websocket("/ws/interview/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket, session_id: str, db: Session = Depends(get_db)
):
    await websocket.accept()

    async def audio_iter():
        try:
            while True:
                data = await websocket.receive_bytes()
                yield data
        except Exception:
            print("Client disconnected")

    await run_pipeline(audio_iter(), websocket, session_id, db)


# Include Routers
app.include_router(auth.router)
app.include_router(adminroutes.router)
app.include_router(guest.router)
app.include_router(interviewroute.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Interview Preparation App!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
