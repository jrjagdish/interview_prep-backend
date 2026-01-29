from typing import List
from pydantic import BaseModel
from app.core.config import settings
# Assuming you use LangChain or direct Groq/OpenAI calls

class QuestionList(BaseModel):
    questions: List[str]

class EvaluationDetail(BaseModel):
    question: str
    answer: str
    score: int # 1-5
    feedback: str

class InterviewResult(BaseModel):
    total_score: float
    overall_feedback: str
    breakdown: List[EvaluationDetail]

class InterviewAgent:
    def __init__(self, groq_api_key: str):
        self.api_key = groq_api_key

    def generate_questions(self, count: int, role: str, level: str, seed: str):
        # We add 'JSON' requirement to the system message
        system_msg = (
            "You are a Senior Technical Interviewer. "
            f"Generate exactly {count} {level}-level interview questions for a {role} position. "
            "Output MUST be a JSON object with a key 'questions' containing a list of strings."
        )
        # In your service: self.agent.generate_questions(...)
        # Ensure you call the model with response_format={"type": "json_object"}
        pass

    def evaluate_answers(self, qa_data: list) -> InterviewResult:
        system_msg = (
            "You are a Technical Lead evaluating a candidate. "
            "Score each answer from 1 to 5. Provide a total average score and a technical summary. "
            "Output MUST be a JSON object matching the InterviewResult schema."
        )
        # qa_data contains the list of {'question': ..., 'answer': ...} 
        # from our InterviewQA table.
        pass


QUESTION_PROMPT = """
You are a senior technical interviewer.
Generate {count} {level}-level backend interview questions for the role "{role}".
{seed_text}

Rules:
- Questions must be conceptual + practical.
- No explanations or extra text.
- No markdown formatting.
"""

EVALUATION_PROMPT = """
You are evaluating a technical interview.
Analyze the candidate's answers based on correctness and depth.

Interview data:
{qa_data}

Rules:
- Be precise and technical.
- Output MUST match the JSON schema exactly.
"""    