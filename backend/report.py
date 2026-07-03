import io
import json
import os

import cloudinary.uploader
from groq import AsyncGroq

import config  # noqa: F401 — configures the cloudinary SDK on import

groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

REPORT_MODEL = "llama-3.3-70b-versatile"

REPORT_SYSTEM_PROMPT = (
    "You are an expert technical interviewer grading a completed job interview "
    "transcript. Evaluate the candidate's answers for relevance, depth, clarity and "
    "communication confidence. Respond with STRICT JSON only (no markdown, no prose "
    "outside the object) matching exactly this schema:\n"
    "{\n"
    '  "total_score": <integer 0-100, overall interview performance>,\n'
    '  "confidence": <integer 0-100, how confident and articulate the candidate sounded>,\n'
    '  "strengths": [<short strings>],\n'
    '  "improvements": [<short strings, concrete and actionable>],\n'
    '  "summary": <2-3 sentence overall assessment>\n'
    "}"
)


def _build_transcript(messages: list[dict]) -> str:
    lines = []
    for m in messages:
        speaker = "Interviewer" if m.get("role") == "assistant" else "Candidate"
        lines.append(f"{speaker}: {m.get('content', '')}")
    return "\n".join(lines)


async def generate_report(messages: list[dict], job_role: str | None) -> dict:
    transcript = _build_transcript(messages)
    user_content = (
        f"Role interviewed for: {job_role or 'unspecified'}\n\n"
        f"Transcript:\n{transcript or '(no responses recorded)'}"
    )

    response = await groq_client.chat.completions.create(
        messages=[
            {"role": "system", "content": REPORT_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        model=REPORT_MODEL,
        temperature=0.3,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


def upload_report(report: dict, interview_id: str) -> str:
    payload = json.dumps(report, indent=2).encode("utf-8")
    result = cloudinary.uploader.upload(
        io.BytesIO(payload),
        resource_type="raw",
        folder="reports",
        public_id=interview_id,
        overwrite=True,
    )
    return result["secure_url"]
