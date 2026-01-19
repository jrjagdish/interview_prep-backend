QUESTION_PROMPT = """
You are a senior backend interviewer.

Generate {count} {level}-level backend interview questions for the role "{role}".

Rules:
- Questions must be conceptual + practical
- No explanations
- No markdown
- No extra text
- Output MUST match the JSON schema exactly
"""

EVALUATION_PROMPT = """
You are evaluating a backend interview.

Analyze the candidate's answers.
Focus on:
- Correctness
- Depth of understanding
- Problem-solving thinking

Rules:
- Do NOT rewrite the answers
- Do NOT praise blindly
- Be precise and technical
- Output MUST match the JSON schema exactly

Interview data:
{qa_data}
"""
