from pydantic import BaseModel

class StartInterviewRequest(BaseModel):
    role: str
    level: str
    guest_id: int | None = None
    user_id: int | None = None

class AnswerRequest(BaseModel):
    answer: str
