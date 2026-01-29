from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_groq import ChatGroq

from app.schemas.ai import QuestionList, EvaluationResult
from app.ai.prompts import QUESTION_PROMPT, EVALUATION_PROMPT

class InterviewAgent:
    def __init__(self, groq_api_key: str):
        # Optimized for speed and JSON reliability
        self.llm = ChatGroq(
            api_key=groq_api_key,
            model="llama-3.3-70b-versatile", # Groq-specific stable model
            temperature=0  # Vital for consistent JSON output
        )

    def generate_questions(self, count: int, level: str, role: str, seed: str | None = None) -> list[str]:
        parser = PydanticOutputParser(pydantic_object=QuestionList)
        
        # We ensure the seed is actually passed as an input variable to the prompt
        prompt = PromptTemplate(
            template=QUESTION_PROMPT + "\n{seed_text}\n{format_instructions}",
            input_variables=["count", "level", "role", "seed_text"],
            partial_variables={
                "format_instructions": parser.get_format_instructions(),
            }
        )

        chain = prompt | self.llm | parser

        seed_value = f"Session seed for uniqueness: {seed}" if seed else ""

        result = chain.invoke({
            "count": count,
            "level": level,
            "role": role,
            "seed_text": seed_value
        })

        return result.questions

    def evaluate_answers(self, qa_data: list[dict]) -> EvaluationResult:
        parser = PydanticOutputParser(pydantic_object=EvaluationResult)

        prompt = PromptTemplate(
            template=EVALUATION_PROMPT + "\n{format_instructions}",
            input_variables=["qa_data"],
            partial_variables={
                "format_instructions": parser.get_format_instructions()
            }
        )

        # LCEL (LangChain Expression Language) chain
        chain = prompt | self.llm | parser

        # We pass the list of dicts; LangChain handles string conversion
        return chain.invoke({
            "qa_data": qa_data
        })