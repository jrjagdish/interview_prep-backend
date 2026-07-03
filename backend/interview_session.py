import json
import os
import time

from redis_client import get_redis

# Hard cap on how long a single interview may run, wall-clock, from the
# moment /api/interviews/start creates the session — it does not pause for
# reconnects, so a dropped connection eats into the interview time rather
# than resetting it.
INTERVIEW_DURATION_SECONDS = int(os.getenv("INTERVIEW_DURATION_SECONDS", "300"))
WARNING_THRESHOLD_SECONDS = 60

# Safety-net TTL so an abandoned session (browser closed, never resumed)
# doesn't sit in Redis forever. Comfortably longer than the interview itself
# so a flaky connection has time to reconnect and finish.
SESSION_TTL_SECONDS = 60 * 60 * 2


def _key(interview_id: str, field: str) -> str:
    return f"interview:{interview_id}:{field}"


async def create_session(interview_id: str, job_role: str | None) -> None:
    r = get_redis()
    now = time.time()
    pipe = r.pipeline()
    pipe.set(_key(interview_id, "started_at"), now, nx=True)
    pipe.set(_key(interview_id, "job_role"), job_role or "", nx=True)
    pipe.set(_key(interview_id, "status"), "active", nx=True)
    for field in ("started_at", "job_role", "status", "messages", "warned"):
        pipe.expire(_key(interview_id, field), SESSION_TTL_SECONDS)
    await pipe.execute()


async def session_exists(interview_id: str) -> bool:
    r = get_redis()
    return bool(await r.exists(_key(interview_id, "started_at")))


async def get_started_at(interview_id: str) -> float | None:
    r = get_redis()
    value = await r.get(_key(interview_id, "started_at"))
    return float(value) if value is not None else None


async def get_job_role(interview_id: str) -> str | None:
    r = get_redis()
    value = await r.get(_key(interview_id, "job_role"))
    return value or None


async def get_remaining_seconds(interview_id: str) -> float:
    started_at = await get_started_at(interview_id)
    if started_at is None:
        return 0.0
    elapsed = time.time() - started_at
    return max(0.0, INTERVIEW_DURATION_SECONDS - elapsed)


async def append_message(interview_id: str, role: str, content: str) -> None:
    r = get_redis()
    payload = json.dumps({"role": role, "content": content, "ts": time.time()})
    key = _key(interview_id, "messages")
    pipe = r.pipeline()
    pipe.rpush(key, payload)
    pipe.expire(key, SESSION_TTL_SECONDS)
    await pipe.execute()


async def get_messages(interview_id: str) -> list[dict]:
    r = get_redis()
    raw = await r.lrange(_key(interview_id, "messages"), 0, -1)
    return [json.loads(item) for item in raw]


async def mark_warned(interview_id: str) -> bool:
    """Returns True the first time it's called for a session, False on later calls."""
    r = get_redis()
    return bool(
        await r.set(_key(interview_id, "warned"), "1", nx=True, ex=SESSION_TTL_SECONDS)
    )


async def end_session(interview_id: str) -> None:
    r = get_redis()
    await r.set(_key(interview_id, "status"), "ended", keepttl=True)
