from pydantic import BaseModel
from typing import List

class QuestionList(BaseModel):
    questions: List[str]

class EvaluationResult(BaseModel):
    score: float
    strengths: List[str]
    weaknesses: List[str]
    feedback: str
