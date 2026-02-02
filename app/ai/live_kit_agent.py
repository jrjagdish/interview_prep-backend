import logging
from uuid import UUID
from livekit import agents
from livekit.agents import voice, llm
from livekit.plugins import deepgram, cartesia, silero

# Your existing logic imports
from app.db.session import SessionLocal
from app.models.users import User,GuestUser
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
        """Custom method to trigger the first question"""
        # 1. Fetch data from DB
        session = self.db.query(InterviewSession).filter(InterviewSession.id == self.interview_id).first()
        
        # 2. Use your existing logic to get a question
        history = [{"q": qa.question_text, "a": qa.user_answer} for qa in session.qa_history]
        questions = self.ai_logic.generate_questions(count=1, level="medium", role="backend", history=history)
        question_text = questions[0]

        # 3. Save to DB
        qa = InterviewQA(session_id=self.interview_id, question_text=question_text)
        self.db.add(qa)
        self.db.commit()

        # 4. Speak it
        await self.session.say(question_text)