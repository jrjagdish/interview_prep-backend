from typing import Any, Dict
from pydantic import BaseModel

class StartInterviewRequest(BaseModel):
    role: str
    level: str

class AnswerRequest(BaseModel):
    answer: str

class InterviewEvaluationOut(BaseModel):
    total_score: int
    overall_feedback: str
    breakdown: Dict[str, Any]

    class Config:
        from_attributes = True    
