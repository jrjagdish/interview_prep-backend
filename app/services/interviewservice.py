from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID, uuid4

from app.models.interview import InterviewSession, InterviewQA
from app.ai.interviewagent import InterviewAgent
from app.core.config import settings

class InterviewService:
    def __init__(self, db: Session):
        self.db = db
        self.agent = InterviewAgent(groq_api_key=settings.GROQ_API_KEY)

    def start_interview_session(
        self,
        role: str,
        level: str,
        admin_id: UUID,
        guest_id: UUID | None = None,
        user_id: UUID | None = None,
    ):
        # 1. Identity Validation
        if not (user_id or guest_id) or (user_id and guest_id):
            raise HTTPException(400, "Provide either user_id or guest_id, not both/neither.")

        # 2. Check for existing active sessions
        owner_filter = InterviewSession.user_id == user_id if user_id else InterviewSession.guest_user_id == guest_id
        existing = self.db.query(InterviewSession).filter(
            owner_filter, 
            InterviewSession.status == "IN_PROGRESS"
        ).first()

        if existing:
            raise HTTPException(400, "An active interview session already exists.")

        # 3. AI Generation (Batch generate questions)
        questions = self.agent.generate_questions(
            count=6, role=role, level=level, seed=f"{user_id or guest_id}-{uuid4()}"
        )

        # 4. Create the Session
        session = InterviewSession(
            admin_id=admin_id,
            user_id=user_id,
            guest_user_id=guest_id,
            total_questions=len(questions),
            current_question_index=0,  # Ensure this matches your Model column name
            status="IN_PROGRESS",
            title=f"{role} ({level}) Interview"
        )
        self.db.add(session)
        self.db.flush()

        # 5. Populate the QA Table
        # NOTE: Added 'question_index' to the loop to match retrieval logic
        for index, q_text in enumerate(questions):
            qa_item = InterviewQA(
                session_id=session.id,
                question_text=q_text,
                question_index=index, # Critical for 'one-at-a-time' logic
            )
            self.db.add(qa_item)

        self.db.commit()

        return {
            "session_id": session.id,
            "question_index": 0,
            "question": questions[0],
        }

    def get_current_question(self, session_id: UUID):
        session = self.db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
        
        if not session:
            raise HTTPException(404, "Session not found")
        
        if session.status == "completed":
            return None, "Interview is finished."

        # Use current_question_index to match start_interview_session
        current_qa = (
            self.db.query(InterviewQA)
            .filter(
                InterviewQA.session_id == session_id,
                InterviewQA.question_index == session.current_question_index
            )
            .first()
        )

        if not current_qa:
            raise HTTPException(404, "Question not found")

        return session.current_question_index, current_qa.question_text

    def submit_answer(self, session_id: UUID, answer_text: str):
        session = self.db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
        
        if not session or session.status == "completed":
            raise HTTPException(400, "Invalid session or interview already completed.")

        # Fetch current record
        qa_record = self.db.query(InterviewQA).filter(
            InterviewQA.session_id == session_id,
            InterviewQA.question_index == session.current_question_index
        ).first()

        if not qa_record or qa_record.user_answer:
            raise HTTPException(400, "Question already answered or invalid index.")

        # Save answer
        qa_record.user_answer = answer_text
        
        # Increment index
        session.current_question_index += 1
        
        # Check if completed
        if session.current_question_index >= session.total_questions:
            session.status = "completed"
            self.db.commit()
            return {"completed": True}
        
        # Fetch the next question string for the frontend
        next_qa = self.db.query(InterviewQA).filter(
            InterviewQA.session_id == session_id,
            InterviewQA.question_index == session.current_question_index
        ).first()

        self.db.commit()
        return {
            "completed": False, 
            "next_index": session.current_question_index,
            "next_question": next_qa.question_text if next_qa else None
        }
    
   