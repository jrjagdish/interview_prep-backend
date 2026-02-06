from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from app.ai.interviewagent import InterviewAgent
from app.models.interview import InterviewSession, InterviewQA
from app.core.config import settings
from app.models.users import Profile
from app.utils.livekit import create_room, create_token


class InterviewService:
    def __init__(self, db: Session):
        self.db = db
        # Pass the API Key to the agent
        # self.ai_agent = InterviewAgent(groq_api_key=settings.GROQ_API_KEY)
        self.MAX_QUESTIONS = 6

    def start_interview_session(
        self,
        role: str,
        level: str,
        admin_id: UUID | None,
        user_id: UUID | None,
        guest_id: UUID | None,
    ):
        session = InterviewSession(..., status="IN_PROGRESS")
        self.db.add(session)
        self.db.commit()

        # 2. Create the LiveKit Room and Token
        room_name = str(session.id)
        create_room(room_name)
        token = create_token(identity=f"user-{session.id}", room_name=room_name)

        # 3. Return the token to the frontend
        # The LIVEKIT AGENT takes over from here!
        return {
            "session_id": session.id, 
            "livekit_token": token
        }