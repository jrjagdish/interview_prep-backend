import asyncio
from dotenv import load_dotenv
from livekit import agents
from livekit.plugins import deepgram, cartesia, silero
from app.ai.live_kit_agent import LiveKitInterviewAgent
from app.db.session import SessionLocal

load_dotenv()

async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()
    
    # 1. Get the Session ID from the room name (assuming room_name == session_id)
    try:
        session_id = ctx.room.name
        db = SessionLocal()
    except Exception as e:
        print(f"Failed to initialize DB: {e}")
        return

    # 2. Setup the Voice Pipeline
    # This automatically handles the audio flow
    session = agents.voice.AgentSession(
        stt=deepgram.STT(),
        tts=cartesia.TTS(),
        vad=silero.VAD.load(),
    )

    # 3. Initialize your Agent
    agent = LiveKitInterviewAgent(db, session_id)

    # 4. Start the session
    await session.start(agent=agent, room=ctx.room)
    
    # 5. Kick off the first question
    await agent.start_interview()

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))