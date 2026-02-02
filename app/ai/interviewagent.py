from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_groq import ChatGroq
from app.schemas.ai import QuestionList, EvaluationResult
from app.ai.prompts import QUESTION_PROMPT, EVALUATION_PROMPT


class InterviewAgent:
    def __init__(self, groq_api_key: str):
        self.llm = ChatGroq(
            api_key=groq_api_key,
            model="llama-3.3-70b-versatile",
            temperature=0.7,  # Temperature 0.7 allows for more natural follow-up questions
        )

    def generate_questions(
        self, count: int, level: str, role: str, history: list = None
    ) -> list[str]:
        parser = PydanticOutputParser(pydantic_object=QuestionList)

        # Format history for the prompt
        history_text = "Previous Q&A:\n"
        if history:
            for item in history:
                history_text += f"Q: {item['q']}\nA: {item['a']}\n"
        else:
            history_text += "None (This is the start of the interview)."

        prompt = PromptTemplate(
            template=QUESTION_PROMPT + "\n{format_instructions}",
            input_variables=["count", "level", "role"],
            partial_variables={
                "format_instructions": parser.get_format_instructions(),
                "history": history_text,
            },
        )

        chain = prompt | self.llm | parser
        result = chain.invoke({"count": count, "level": level, "role": role})
        return result.questions

    def evaluate_single_answer(self, question: str, answer: str) -> EvaluationResult:
        parser = PydanticOutputParser(pydantic_object=EvaluationResult)

        prompt = PromptTemplate(
            template=EVALUATION_PROMPT + "\n{format_instructions}",
            input_variables=["q", "a"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        chain = prompt | self.llm | parser
        return chain.invoke({"q": question, "a": answer})
