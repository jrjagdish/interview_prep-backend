import logging
from uuid import UUID
from livekit import agents
from livekit.agents import voice, llm
from livekit.plugins import deepgram, cartesia, silero

# Your existing logic imports
from app.db.session import SessionLocal
from app.models.users import User, GuestUser
from app.models.interview import InterviewSession, InterviewQA
from app.ai.interviewagent import InterviewAgent
from app.core.config import settings

logger = logging.getLogger(__name__)


class LiveKitInterviewAgent(voice.Agent):
    def __init__(self, db_session, interview_id):
        super().__init__(
            instructions="You are a professional technical interviewer. Ask one question at a time and wait for the user to answer."
        )
        self.db = db_session
        self.interview_id = interview_id
        self.ai_logic = InterviewAgent(groq_api_key=settings.GROQ_API_KEY)

    async def start_interview(self):
        """Fetch the first question already created by the service and speak it."""
        # 1. Fetch the session and the existing first question
        session = (
            self.db.query(InterviewSession)
            .filter(InterviewSession.id == self.interview_id)
            .first()
        )

        # Get the latest QA entry (which was created in InterviewService)
        # We sort by question_index to make sure we get the current one
        qa = (
            self.db.query(InterviewQA)
            .filter(InterviewQA.session_id == self.interview_id)
            .order_by(InterviewQA.question_index.desc())
            .first()
        )

        if qa:
            # 2. Just speak the text that is already in the DB
            await self.session.say(qa.question_text)
        else:
            # Fallback if for some reason the service didn't create it
            fallback_q = "Hello! I'm your interviewer. Can you tell me about yourself?"
            await self.session.say(fallback_q)
