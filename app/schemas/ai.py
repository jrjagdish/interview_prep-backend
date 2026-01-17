from pydantic import BaseModel
from typing import List

class QuestionList(BaseModel):
    questions: List[str]

class EvaluationResult(BaseModel):
    total_score: float
    strengths: List[str]
    weaknesses: List[str]
    overall_feedback: str
