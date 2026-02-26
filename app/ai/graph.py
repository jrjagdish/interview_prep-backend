from langgraph.graph import StateGraph
from app.ai.graph_state import InterviewGraphState
from app.ai.nodes import *

graph = StateGraph(InterviewGraphState)

graph.add_node("intro", intro_node)
graph.add_node("question", question_node)
graph.add_node("wait", wait_for_answer)
graph.add_node("evaluate", evaluate_node)
graph.add_node("decision", decision_node)

graph.set_entry_point("intro")

graph.add_edge("intro", "question")
graph.add_edge("question", "wait")
graph.add_edge("wait", "evaluate")
graph.add_edge("evaluate", "decision")

interview_graph = graph.compile(
    interrupt_before=["decision"]
)