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
        self.ai_agent = InterviewAgent(groq_api_key=settings.GROQ_API_KEY)
        self.MAX_QUESTIONS = 6

    def start_interview_session(
        self,
        role: str,
        level: str,
        admin_id: UUID | None,
        user_id: UUID | None,
        guest_id: UUID | None,
    ):
        if user_id is None and guest_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Identity missing."
            )

        title = f"{level.capitalize()} {role.capitalize()} Mock Interview"
        session = InterviewSession(
            user_id=user_id,
            guest_user_id=guest_id,
            admin_id=admin_id,
            title=title,
            current_question_index=0,
            status="IN_PROGRESS",
        )
        self.db.add(session)
        self.db.flush()

        room_name = str(session.id)
        create_room(room_name)

        token = create_token(identity=f"user-{session.id}", room_name=room_name)

        questions = self.ai_agent.generate_questions(count=1, level=level, role=role)
        first_q = (
            questions[0] if questions else "Can you tell me about your experience?"
        )

        qa_entry = InterviewQA(
            session_id=session.id, question_text=first_q, question_index=0
        )
        self.db.add(qa_entry)
        self.db.commit()
        data = self.db.query(Profile).filter(Profile.user_id == user_id).first()
        if data.interview_credits <= 0:
            raise HTTPException(
                status_code=400, detail="Insufficient interview credits."
            )
        else:
            data.interview_credits -= 1
            self.db.commit()

        return {"session_id": session.id, "title": session.title, "question": first_q , "livekit_token": token}

    def submit_answer(self, session_id: UUID, answer: str):
        session = (
            self.db.query(InterviewSession)
            .filter(InterviewSession.id == session_id)
            .first()
        )
        if not session or session.status == "COMPLETED":
            raise HTTPException(status_code=400, detail="Session inactive.")

        qa_entry = (
            self.db.query(InterviewQA)
            .filter(
                InterviewQA.session_id == session_id,
                InterviewQA.question_index == session.current_question_index,
            )
            .first()
        )

        if not qa_entry:
            raise HTTPException(404, "Question not found")

        eval_result = self.ai_agent.evaluate_single_answer(
            qa_entry.question_text, answer
        )

        qa_entry.user_answer = answer
        qa_entry.ai_feedback = eval_result.feedback
        qa_entry.score = eval_result.score

        session.current_question_index += 1
        completed = session.current_question_index >= self.MAX_QUESTIONS

        next_question_text = None
        if not completed:

            history = [
                {"q": qa.question_text, "a": qa.user_answer}
                for qa in session.qa_history
                if qa.user_answer
            ]
            next_q_list = self.ai_agent.generate_questions(
                count=1, level=session.title, role="", history=history
            )
            next_question_text = next_q_list[0]

            # Save the next question to DB
            next_qa = InterviewQA(
                session_id=session.id,
                question_text=next_question_text,
                question_index=session.current_question_index,
            )
            self.db.add(next_qa)
        else:
            session.status = "COMPLETED"

        self.db.commit()

        return {
            "ai_feedback": qa_entry.ai_feedback,
            "score": qa_entry.score,
            "next_question": next_question_text,
            "completed": completed,
        }
