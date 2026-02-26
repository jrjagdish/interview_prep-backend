import requests
from app.core.config import settings

def speak(text: str) -> bytes:
    r = requests.post(
        "https://api.cartesia.ai/tts",
        headers={"Authorization": f"Bearer {settings.CARTESIA_API_KEY}"},
        json={
            "text": text,
            "voice": "neutral",
            "format": "mp3"
        }
    )
    return r.content