from openai import AsyncOpenAI
from app.core.config import settings

client = AsyncOpenAI(api_key=settings.GROQ_API_KEY)

async def call_llm(system: str, user: str, max_tokens: int) -> str:
    resp = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        temperature=0.3,
        max_tokens=max_tokens
    )
    return resp.choices[0].message.content.strip()