from enum import Enum

class InterviewState(str, Enum):
    CONNECTED = "CONNECTED"
    INTRO = "INTRO"
    QUESTION = "QUESTION"
    ANSWER = "ANSWER"
    EVALUATION = "EVALUATION"
    DECISION = "DECISION"
    END = "END"