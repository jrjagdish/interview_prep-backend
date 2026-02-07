import logging
import json
from datetime import datetime
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
)

from livekit.plugins import noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")
load_dotenv(".env.local")

# --- NEW: THIS FUNCTION SAVES THE DATA WHEN THE SESSION ENDS ---
async def on_session_end(ctx: JobContext) -> None:
    # 1. Get the full summary of the talk
    report = ctx.make_session_report()
    report_dict = report.to_dict()

    # 2. Write it to response.txt
    # We use 'a' for append so it doesn't delete previous interviews
    with open("response.txt", "a") as f:
        f.write(f"\n--- Interview Session: {ctx.room.name} ---\n")
        f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Write the actual messages (the transcript)
        for msg in report_dict.get("messages", []):
            role = msg.get("role")
            content = msg.get("content")
            f.write(f"{role.upper()}: {content}:{msg}\n")
        
        f.write("-" * 30 + "\n")

    print(f"✅ Success! Conversation for {ctx.room.name} saved to response.txt")

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a helpful voice AI assistant. 
            Keep responses concise, friendly, and without complex formatting.""",
        )

server = AgentServer()

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

server.setup_fnc = prewarm

# --- UPDATED: ADDED THE on_session_end TRIGGER HERE ---
@server.rtc_session(on_session_end=on_session_end)
async def my_agent(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}

    session = AgentSession(
        stt=inference.STT(model="deepgram/nova-3", language="multi"),
        llm=inference.LLM(model="openai/gpt-4o-mini"), # Changed to o-mini for speed
        tts=inference.TTS(model="cartesia/sonic-3", voice="9626c31c-bec5-4cca-baa8-f8ba9e84c8bc"),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    await session.start(
        agent=Assistant(),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: noise_cancellation.BVC(),
            ),
        ),
    )

    await ctx.connect()

if __name__ == "__main__":
    cli.run_app(server)