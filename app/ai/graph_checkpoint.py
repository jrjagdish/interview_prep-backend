import time
from app.ai.redis_client import set_json, get_json, delete

def save_checkpoint(session_id: str, data: dict):
    set_json(f"graph:{session_id}", {
        **data,
        "updated_at": time.time()
    })

def load_checkpoint(session_id: str):
    return get_json(f"graph:{session_id}")

def delete_checkpoint(session_id: str):
    delete(f"graph:{session_id}")