from pydantic import BaseModel

class StartInterviewRequest(BaseModel):
    role: str
    level: str

class AnswerRequest(BaseModel):
    answer: str
