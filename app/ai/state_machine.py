from schemas import InterviewState

def next_state(current: InterviewState, event: str):
    transitions = {
        InterviewState.CONNECTED: {"auto": InterviewState.INTRO},
        InterviewState.INTRO: {"intro_sent": InterviewState.QUESTION},
        InterviewState.QUESTION: {"question_sent": InterviewState.ANSWER},
        InterviewState.ANSWER: {"answer_received": InterviewState.EVALUATION},
        InterviewState.EVALUATION: {"evaluation_done": InterviewState.DECISION},
        InterviewState.DECISION: {
            "continue": InterviewState.QUESTION,
            "stop": InterviewState.END
        }
    }
    return transitions[current][event]