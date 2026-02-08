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

def my_llm_node(state: State):
    llm = ChatGroq(model="openai/gpt-oss-120b")
    response = llm.invoke(state["messages"])
    
    # 3. Return the AIMessage object directly
    return {"messages": [response]} 

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
    graph = create_graph()

    langgraph_llm = langchain.LLMAdapter(graph=graph)

    session = AgentSession(
        stt=inference.STT(model="deepgram/nova-3", language="multi"),
        llm=langgraph_llm, # Changed to o-mini for speed
        tts=inference.TTS(model="cartesia/sonic-3", voice="9626c31c-bec5-4cca-baa8-f8ba9e84c8bc"),
        # turn_detection=MultilingualModel(),
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
    await session.say("Connected and ready.", allow_interruptions=True)

    await ctx.connect()

if __name__ == "__main__":
    cli.run_app(server)