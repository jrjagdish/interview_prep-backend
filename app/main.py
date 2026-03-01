# from fastapi import FastAPI, WebSocket
# from fastapi.middleware.cors import CORSMiddleware
# from app.ai.websocket import interview_socket
# from app.ai.websocket import interview_socket
# from app.db.init import init_db
# from app.routes import auth, adminroutes, guest,interviewroute


# app = FastAPI(title="Interview Preparation App")
# @app.on_event("startup")
# def on_startup():
#     init_db()
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000", "http://127.0.0.1:3000","http://127.0.0.1:8000","http://localhost:5173"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# @app.websocket("/ws/interview")
# async def interview(ws: WebSocket):
#     await interview_socket(ws)
# app.include_router(auth.router)
# app.include_router(adminroutes.router)
# app.include_router(guest.router)

# app.include_router(interviewroute.router)
# @app.get("/")
# def read_root():
#     return {"message": "Welcome to the Interview Preparation App!"}
import asyncio
import os
import json
import base64
from typing import AsyncIterator
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

# Import the helper classes from your local files 
# (Or paste the class definitions here if they aren't in the path)
from app.ai.assemblyai_stt import AssemblyAISTT
from app.ai.tts_cartesia import CartesiaTTS
from app.utils.helper import merge_async_iters
from app.utils.events import STTOutputEvent, AgentChunkEvent, AgentEndEvent, event_to_dict
from fastapi.middleware.cors import CORSMiddleware



# Add this block right after 'app = FastAPI()'


load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, replace "*" with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. THE BRAIN (LLM)
llm = ChatGroq(model="llama-3.3-70b-versatile", streaming=True)

async def interview_brain(transcript: str) -> AsyncIterator:
    """Processes text and yields streaming agent chunks."""
    system_prompt = "You are a friendly technical interviewer. Keep responses under 2 sentences."
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=transcript)
    ]
    
    async for chunk in llm.astream(messages):
        yield AgentChunkEvent.create(chunk.content)
    yield AgentEndEvent.create()

async def run_pipeline(audio_stream: AsyncIterator[bytes], websocket: WebSocket):
    stt = AssemblyAISTT(sample_rate=16000)
    tts = CartesiaTTS()

    # TASK A: Listen to the Microphone and send to AssemblyAI
    async def stt_sender():
        try:
            async for chunk in audio_stream:
                await stt.send_audio(chunk)
        finally:
            await stt.close()

    # TASK B: Listen for synthesized audio from Cartesia and send to Browser
    async def tts_receiver():
        async for tts_event in tts.receive_events():
            await websocket.send_json(event_to_dict(tts_event))

    # Fire off background tasks
    asyncio.create_task(stt_sender())
    asyncio.create_task(tts_receiver())

    # MAIN LOOP: Process Transcripts -> LLM -> TTS Trigger
    try:
        async for stt_event in stt.receive_events():
            # Send ALL stt events (chunks + output) to frontend
            await websocket.send_json(event_to_dict(stt_event))

            if isinstance(stt_event, STTOutputEvent):
                print(f"DEBUG: Processing Transcript: {stt_event.transcript}")
                
                text_buffer = []
                async for agent_event in interview_brain(stt_event.transcript):
                    await websocket.send_json(event_to_dict(agent_event))
                    
                    if isinstance(agent_event, AgentChunkEvent):
                        text_buffer.append(agent_event.text)
                    
                    if isinstance(agent_event, AgentEndEvent):
                        # Trigger TTS - Task B will catch the resulting audio
                        await tts.send_text("".join(text_buffer))
    finally:
        await tts.close()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    async def audio_iter():
        try:
            while True:
                data = await websocket.receive_bytes()
                yield data
        except Exception:
            print("Client disconnected")

    await run_pipeline(audio_iter(), websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)