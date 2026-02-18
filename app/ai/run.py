from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Dict
from app.core.config import settings
# 1. Define the output structure
class Evaluation(BaseModel):
    feedback: str = Field(description="Detailed, critical feedback on the user's performance.")
    score: int = Field(description="A strict score out of 100 based on the quality of the interaction.")

async def evaluate(history: str) -> Evaluation:
    
    llm = ChatGroq(
        temperature=0, 
        model_name="llama-3.3-70b-versatile",
        groq_api_key= settings.GROQ_API_KEY
    )

  
    structured_llm = llm.with_structured_output(Evaluation)

 
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a strict, high-standard professional evaluator. "
            "Analyze the following interview/chat history. "
            "Be critical: point out logical fallacies, weak communication, or lack of depth. "
            "Provide a score out of 100 where 100 is perfection and 50 is a failing grade."
        )),
        ("human", "Evaluate this history: {history}")
    ])

   
    chain = prompt | structured_llm
    result = await chain.ainvoke({"history": history})
    
    return result.score, result.feedback

