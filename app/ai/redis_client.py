import redis
import json
REDIS_URL = "redis://localhost:6379"

redis_client = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True
)

def set_json(key: str, value: dict):
    redis_client.set(key, json.dumps(value))

def get_json(key: str):
    data = redis_client.get(key)
    return json.loads(data) if data else None

def delete(key: str):
    redis_client.delete(key)