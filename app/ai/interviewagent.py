from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_groq import ChatGroq

from app.schemas.ai import QuestionList, EvaluationResult
from app.ai.prompts import QUESTION_PROMPT, EVALUATION_PROMPT


class InterviewAgent:
    def __init__(self, groq_api_key: str):
        self.llm = ChatGroq(
            api_key=groq_api_key,
            model="openai/gpt-oss-120b",
            temperature=0
        )

    def generate_questions(self, count: int, level: str, role: str) -> list[str]:
        parser = PydanticOutputParser(pydantic_object=QuestionList)

        prompt = PromptTemplate(
            template=QUESTION_PROMPT + "\n{format_instructions}",
            input_variables=["count", "level", "role"],
            partial_variables={
                "format_instructions": parser.get_format_instructions()
            }
        )

        chain = prompt | self.llm | parser

        result = chain.invoke({
            "count": count,
            "level": level,
            "role": role
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

        chain = prompt | self.llm | parser

        return chain.invoke({
            "qa_data": qa_data
        })
