# app/ai/graph_runner.py

import asyncio
from app.ai.graph import interview_graph
from app.ai.graph_checkpoint import save_checkpoint


async def run_graph(session_id: str, websocket):
    """
    Runs the LangGraph in the background.
    Sends AI messages to the client WITHOUT blocking the WebSocket.
    """

    async for event in interview_graph.astream(
        {"session_id": session_id},
        stream_mode="values"
    ):
        # 🔹 Only proceed if state exists
        state = event.get("state")

        if not state:
            continue  # ignore events without state

        # Save checkpoint safely
        await save_checkpoint(session_id, state)

        # Send AI message if present
        ai_message = state.get("ai_message")
        if ai_message:
            await websocket.send_json({
                "type": "ai_message",
                "text": ai_message
            })

        # Send evaluation if present
        evaluation = state.get("evaluation")
        if evaluation:
            await websocket.send_json({
                "type": "evaluation",
                "scores": evaluation
            })