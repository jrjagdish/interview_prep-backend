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
    llm
)

from livekit.plugins import noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from typing import Annotated, TypedDict, Union

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from livekit.plugins import langchain, silero
from langchain_groq import ChatGroq


logger = logging.getLogger("agent")
load_dotenv(".env.local")
load_dotenv(".env")

class State(TypedDict):
    # 'messages' is the standard key LangGraph uses for chat history
    messages: Annotated[list, add_messages]
    question_count: int

def my_llm_node(state: State):
    count = state.get("question_count", 0)
    _llm = ChatGroq(model="openai/gpt-oss-120b")
    response = _llm.invoke(state["messages"])
    if count >= 6:
        return {
            "messages": [("ai", "We have covered 6 questions today, which completes our session. Thank you!")],
            "question_count": count
        }
    # 3. Return the AIMessage object directly
    return {"messages": [response],"question_count": count + 1} 

def create_graph():
    workflow = StateGraph(State)
    workflow.add_node("agent", my_llm_node)
    workflow.add_edge(START, "agent")
    workflow.add_edge("agent", END)
    return workflow.compile()  

# --- NEW: THIS FUNCTION SAVES THE DATA WHEN THE SESSION ENDS ---
async def on_session_end(ctx: JobContext) -> None:
    # 1. Get the full summary of the talk
    report = ctx.make_session_report()
    
    # 2. Dump everything to the file
    with open("response.txt", "a", encoding="utf-8") as f:
        f.write(f"\n--- NEW SESSION DUMP: {datetime.now()} ---\n")
        # Convert the report object to a dictionary and then a formatted JSON string
        f.write(json.dumps(report.to_dict(), indent=2))
        f.write("\n" + "="*50 + "\n")

    print(f"✅ Full session dump saved for room: {ctx.room.name}")

# ... (your imports and Graph code stay the same) ...

class Assistant(Agent):
    def __init__(self, user_id: str = "Unknown", user_name: str = "Guest") -> None:
        super().__init__(
            instructions=f"""You are a helpful voice AI assistant. 
            You are currently talking to {user_name} (ID: {user_id}).
            Keep responses concise, friendly, and without complex formatting.""",
        )
server = AgentServer()

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

server.setup_fnc = prewarm        

@server.rtc_session(on_session_end=on_session_end)
async def my_agent(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}
    
    # 1. Connect to the room first
    await ctx.connect()
    
    # 2. Identify the user (assuming one human user joins)
    # We wait a brief moment or check the participants already in the room
    user_id = "unknown"
    user_name = "Guest"
    
    # Check if a participant is already there or wait for one
    if ctx.room.remote_participants:
        p = next(iter(ctx.room.remote_participants.values()))
        try:
            metadata = json.loads(p.metadata)
            user_id = metadata.get("user_id", "unknown")
            user_name = p.name or "User"
            logger.info(f"Detected User: {user_id} ({user_name})")
        except:
            logger.warning("Could not parse participant metadata")

    # 3. Setup Graph and LLM
    graph = create_graph()
    langgraph_llm = langchain.LLMAdapter(graph=graph)

    session = AgentSession(
        stt=inference.STT(model="deepgram/nova-3", language="multi"),
        llm=langgraph_llm,
        tts=inference.TTS(model="cartesia/sonic-3", voice="9626c31c-bec5-4cca-baa8-f8ba9e84c8bc"),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    @session.on("agent_speech_committed")
    def on_speech_committed(msg: llm.ChatMessage):
        content = msg.content.lower()
        if "goodbye" in content or "interview is now complete" in content:
            logger.info("Final question reached. Shutting down...")
            ctx.shutdown()

    # 4. Start session with the personalized Assistant
    await session.start(
        agent=Assistant(user_id=user_id, user_name=user_name),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: noise_cancellation.BVC(),
            ),
        ),
    )

    await session.say(f"Hello {user_name}, I'm ready to help.", allow_interruptions=True)



if __name__ == "__main__":
    cli.run_app(server)