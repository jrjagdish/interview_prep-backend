import json
from app.ai.llm_client import call_llm

async def intro_node(state):
    return {
        **state,
        "messages": state["messages"] + [{
            "from": "ai",
            "text": "Welcome. Let’s begin your technical interview."
        }]
    }

async def question_node(state):
    question = await call_llm(
        "Ask ONE concise technical interview question.",
        f"Role: {state['role']}",
        max_tokens=120
    )

    return {
        **state,
        "current_question": question,
        "messages": state["messages"] + [{
            "from": "ai",
            "text": question
        }],
        "token_usage": state["token_usage"] + 120
    }

async def wait_for_answer(state):
    return state

async def evaluate_node(state):
    prompt = f"""
Evaluate the following answer. 
Return STRICT JSON with scores from 0–10.

Question: {state['current_question']}
Answer: {state['messages'][-1]['text']}

JSON FORMAT:
{{
  "technical_depth": int,
  "clarity": int,
  "correctness": int,
  "confidence": int
}}
"""

    raw = await call_llm(
        "You are a strict technical interviewer.",
        prompt,
        max_tokens=200
    )

    scores = json.loads(raw)
    overall = sum(scores.values()) / 4

    hire_signal = (
        "STRONG" if overall >= 8 else
        "WEAK" if overall >= 5 else
        "REJECT"
    )

    return {
        **state,
        "evaluation": {
            **scores,
            "overall_score": round(overall, 1),
            "hire_signal": hire_signal
        },
        "token_usage": state["token_usage"] + 200
    }

async def decision_node(state):
    return state