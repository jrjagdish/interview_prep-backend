from pydantic import BaseModel
from typing import List,TypedDict

class QuestionList(BaseModel):
    questions: List[str]

class EvaluationResult(BaseModel):
    score: float
    strengths: List[str]
    weaknesses: List[str]
    feedback: str


