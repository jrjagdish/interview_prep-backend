from langgraph.graph import StateGraph,START,END
from langchain_groq import ChatGroq
from app.ai.state import InterviewState




class InterviewAgentGraph(StateGraph):
    def __init__(self,groq_api_key:str):
        self.llm = ChatGroq(model="openai/gpt-oss-120b", api_key=groq_api_key)
        workflow = StateGraph(InterviewState)
        workflow.add_node("interviewer",self.call_llm)
        workflow.set_entry_point("interviewer")

        workflow.add_edge("interviewer",END)

        self.app = workflow.compile()

    async def call_llm(self,state:InterviewState):
        prompt = f"""You are a senior technical interviewer for a {state['role']} position ({state['level']}).
        - If the user just joined, introduce yourself and ask a foundational question.
        - If the user answered a question, evaluate if it's sufficient. 
        - If it's shallow, ask a follow-up (e.g., 'Can you expand on how that works under the hood?').
        - If it's good, move to a new topic.
        - Keep responses concise for voice interaction."""
        messages = [{"role": "system", "content": prompt}]+state['messages']
        response = await self.llm.ainvoke(messages)
        return {"messages":[response]}

