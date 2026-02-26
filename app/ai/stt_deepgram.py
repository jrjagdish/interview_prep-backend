from deepgram import DeepgramClient
from app.core.config import settings
DEEPGRAM_API_KEY = settings.DEEPGRAM_API_KEY

dg = DeepgramClient(DEEPGRAM_API_KEY)

def transcribe(audio_bytes: bytes) -> str:
    response = dg.listen.prerecorded.v("1").transcribe_file(
        {"buffer": audio_bytes},
        {"model": "nova-2"}
    )
    return response["results"]["channels"][0]["alternatives"][0]["transcript"]