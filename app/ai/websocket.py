import uuid
import asyncio
from fastapi import WebSocket
from app.ai.graph_runner import run_graph
from app.ai.graph_checkpoint import load_checkpoint, save_checkpoint

async def interview_socket(ws: WebSocket):
    await ws.accept()
    session_id = str(uuid.uuid4())

    state = {
        "session_id": session_id,
        "role": "backend",
        "messages": [],
        "current_question": None,
        "evaluation": None,
        "recruiter_override": False,
        "token_usage": 0
    }

    save_checkpoint(session_id, {
        "state": state,
        "node": "intro",
        "paused": False
    })

    async def send_event(payload):
        await ws.send_json(payload)

    # 🔥 RUN GRAPH IN BACKGROUND
    asyncio.create_task(run_graph(session_id, state, send_event))

    while True:
        data = await ws.receive_json()

        checkpoint = load_checkpoint(session_id)
        checkpoint["state"]["messages"].append({
            "from": "candidate",
            "text": data["text"]
        })

        save_checkpoint(session_id, checkpoint)

        asyncio.create_task(
            run_graph(session_id, checkpoint["state"], send_event)
        )