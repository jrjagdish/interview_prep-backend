import json
from livekit.api import LiveKitAPI, ListRoomsRequest
import os
from fastapi import APIRouter, Request
from livekit import api
from dotenv import load_dotenv
import uuid

load_dotenv()


def create_token_for_room(user_id: str, session_id: str, role: str, user_name: str):
    metadata = json.dumps({"user_id": user_id, "session_id": session_id, "role": role})
    token = (
        api.AccessToken(os.getenv("LIVEKIT_API_KEY"), os.getenv("LIVEKIT_API_SECRET"))
        .with_identity(user_id)
        .with_name(user_name)
        .with_metadata(metadata)
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room=f"my-{session_id}",
            )
        )
        .to_jwt()
    )
    return token
