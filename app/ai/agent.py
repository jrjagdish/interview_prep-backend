import logging
import json
import asyncio
import re
from datetime import datetime
import uuid
from dotenv import load_dotenv

from livekit import rtc
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    cli,
    inference,
    room_io,
    llm,
)

from livekit.plugins import noise_cancellation, silero, langchain
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq

from app.db.session import SessionLocal
from app.models.interview import InterviewQA, InterviewSession
# --- CRITICAL FIX: Import related models to resolve SQLAlchemy relationships ---
from app.models.users import User, GuestUser 

logger = logging.getLogger("agent")
load_dotenv()

server = AgentServer()

class State(TypedDict):
    messages: Annotated[list, add_messages]
    question_count: int

def my_llm_node(state: State):
    count = state.get("question_count", 0)

    if count >= 6:
        return {
            "messages": [
                (
                    "ai",
                    "That was the final question. Thank you for your time today. Goodbye.",
                )
            ],
            "question_count": count,
        }

    # --- PERFORMANCE FIX: Switched to a faster, high-quality model ---
    llm_model = ChatGroq(model="llama-3.3-70b-versatile")
    response = llm_model.invoke(state["messages"])

    return {
        "messages": [response],
        "question_count": count + 1,
    }

def create_graph():
    g = StateGraph(State)
    g.add_node("agent", my_llm_node)
    g.add_edge(START, "agent")
    g.add_edge("agent", END)
    return g.compile()

async def on_session_end(ctx: JobContext):
    report = ctx.make_session_report()
    data = report.to_dict()
    db = SessionLocal()

    try:
        raw_name = ctx.room.name
        uuid_match = re.search(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', raw_name)
        
        if not uuid_match:
            logger.error(f"❌ No valid UUID in room: {raw_name}")
            return
            
        session_uuid = uuid.UUID(uuid_match.group(0))

        # Mark session completed
        db.query(InterviewSession).filter(InterviewSession.id == session_uuid).update(
            {"status": "COMPLETED", "completed_at": datetime.utcnow()}
        )

        history_items = data.get("chat_history", {}).get("items", [])
        question_index = 0

        for item in history_items:
            if item.get("type") != "message":
                continue 

            role = item.get("role") 
            text = " ".join(item.get("content", [])).strip()

            if not text:
                continue

            db.add(
                InterviewQA(
                    session_id=session_uuid,
                    question_index=question_index,
                    chat_history=json.dumps({"role": role, "text": text}),
                )
            )
            question_index += 1

        db.commit()
        logger.info(f"✅ Interview {session_uuid} saved to database.")
    except Exception as e:
        logger.error(f"❌ Database error: {e}")
    finally:
        db.close()

class Assistant(Agent):
    def __init__(self, user_name: str):
        super().__init__(
            instructions=f"""
You are a professional technical interviewer.
1. Talk to {user_name}.
2. Ask exactly ONE technical question at a time.
3. You must WAIT for the user to finish their answer before asking the next question.
4. If the user's answer is too brief, you may ask a follow-up, but keep the total questions to 6.
5. After 6 questions, say goodbye.
"""
        )

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

server.setup_fnc = prewarm

@server.rtc_session(on_session_end=on_session_end)
async def my_agent(ctx: JobContext):
    await ctx.connect()

    participant = await ctx.wait_for_participant()
    user_name = participant.name or "Candidate"

    logger.info(f"Interview started with {user_name}")

    graph = create_graph()
    langgraph_llm = langchain.LLMAdapter(graph=graph)

    session = AgentSession(
        stt=inference.STT(model="deepgram/nova-3"),
        llm=langgraph_llm,
        tts=inference.TTS(model="cartesia/sonic-3"),
        vad=ctx.proc.userdata["vad"],
        min_endpointing_delay=1.5,
        preemptive_generation=False,
    )

    @session.on("agent_speech_committed")
    def on_ai(msg: llm.ChatMessage):
        state = (msg.metadata or {}).get("state", {})
        if state.get("question_count", 0) >= 6:
            async def shutdown():
                await asyncio.sleep(2.0)
                ctx.shutdown()
            asyncio.create_task(shutdown())

    @ctx.room.on("participant_disconnected")
    def on_left(_):
        ctx.shutdown()

    await session.start(
        agent=Assistant(user_name),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda _: noise_cancellation.BVC(),
            ),
        ),
    )

    await session.say(
        f"Hello {user_name}, I'm your AI interviewer. Let's start the session.",
        allow_interruptions=True,
    )

if __name__ == "__main__":
    cli.run_app(server)