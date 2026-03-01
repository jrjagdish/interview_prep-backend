from typing import TypedDict, List, Dict, Optional

class EvaluationResult(TypedDict):
    technical_depth: int
    clarity: int
    correctness: int
    confidence: int
    overall_score: float
    hire_signal: str

class InterviewGraphState(TypedDict):
    session_id: str
    role: str
    messages: List[dict]
    current_question: Optional[str]
    evaluation: Optional[EvaluationResult]
    recruiter_override: bool
    token_usage: int