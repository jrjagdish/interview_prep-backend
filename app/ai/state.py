from typing import TypedDict, List,Annotated
from langgraph.graph.message import add_messages

class InterviewState(TypedDict):
    messages : Annotated[List[dict], add_messages]
    covered_questions: List[str]
    role:str
    level:str
    is_finished : bool
    