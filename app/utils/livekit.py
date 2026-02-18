from livekit import api
from app.core.config import settings

lk_api = api.LiveKitAPI(
    settings.LIVEKIT_URL,
    settings.LIVEKIT_API_KEY,
    settings.LIVEKIT_API_SECRET,
)

def create_room(room_name: str):
    try:
        lk_api.room.create(api.CreateRoomRequest(name=room_name))
    except Exception:
        pass  # room already exists

def create_token(identity: str, room_name: str):
    token = api.AccessToken(
        settings.LIVEKIT_API_KEY,
        settings.LIVEKIT_API_SECRET,
    ).with_identity(identity).with_grants(
        api.VideoGrants(
            room_join=True,
            room=room_name,
        )
    )
    return token.to_jwt()
