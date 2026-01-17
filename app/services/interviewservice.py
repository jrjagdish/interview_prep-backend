from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.interviewevaluation import InterviewEvaluation
from app.models.interviewanswer import InterviewAnswer
from app.models.interviewquestion import InterviewQuestion
from app.models.interviewsession import InterviewSession
from app.ai.interviewagent import InterviewAgent
from app.core.config import settings
from uuid import UUID


class InterviewService:
    def __init__(self, db: Session):
        self.db = db
        self.agent = InterviewAgent(groq_api_key=settings.GROQ_API_KEY)

    def start_interview_session(
        self,
        role: str,
        level: str,
        guest_id: UUID | None = None,
        user_id: UUID | None = None,
    ):
        if guest_id and user_id:
            raise HTTPException(400, "Invalid identity")

        # ---------------- USER FLOW ----------------
        if user_id:
            existing = (
                self.db.query(InterviewSession)
                .filter(
                    InterviewSession.user_id == user_id,
                    InterviewSession.status == "IN_PROGRESS",
                )
                .first()
            )

        # ---------------- GUEST FLOW ----------------
        else:
            existing = (
                self.db.query(InterviewSession)
                .filter(
                    InterviewSession.guest_user_id == guest_id,
                    InterviewSession.status == "IN_PROGRESS",
                )
                .first()
            )

        if existing:
            raise HTTPException(400, "Active interview already exists")

        # Generate questions
        questions = self.agent.generate_questions(count=6, role=role, level=level)

        session = InterviewSession(
            user_id=user_id,
            guest_user_id=guest_id,
            total_questions=len(questions),
            current_question_index=0,
            status="IN_PROGRESS",
        )

        self.db.add(session)
        self.db.flush()

        for index, question_text in enumerate(questions):
            self.db.add(
                InterviewQuestion(
                    session_id=session.id,
                    question_index=index,
                    question_text=question_text,
                )
            )

        self.db.commit()

        return {
            "session_id": session.id,
            "question_index": 0,
            "question": questions[0],
        }

    # ---------------- INTERVIEW FLOW ---------------- #

    def get_current_question(self, session_id: int):
        session = self._get_active_session(session_id)
        question = (
            self.db.query(InterviewQuestion)
            .filter_by(
                session_id=session.id, question_index=session.current_question_index
            )
            .first()
        )

        return session.current_question_index, question.question_text

    def submit_answer(self, session_id: int, answer: str) -> bool:
        with self.db.begin():  # transaction boundary

            # Lock session row
            session = (
                self.db.query(InterviewSession)
                .filter(
                    InterviewSession.id == session_id,
                    InterviewSession.status == "IN_PROGRESS",
                )
                .with_for_update()
                .first()
            )

        if not session:
            raise HTTPException(404, "Session not active")

        # Fetch current question
        question = (
            self.db.query(InterviewQuestion)
            .filter_by(
                session_id=session.id,
                question_index=session.current_question_index,
            )
            .first()
        )

        if not question:
            raise HTTPException(400, "Invalid question index")

        # Prevent duplicate answer
        existing = (
            self.db.query(InterviewAnswer)
            .filter_by(
                session_id=session.id,
                question_id=session.current_question_index,
            )
            .first()
        )

        if existing:
            raise HTTPException(409, "Answer already submitted")

        # Save answer
        self.db.add(
            InterviewAnswer(
                session_id=session.id,
                question_id=session.current_question_index,
                answer_text=answer,
            )
        )

        # Move to next question
        session.current_question_index += 1

        if session.current_question_index >= session.total_questions:
            session.status = "COMPLETED"

        # commit happens automatically here
        return session.status == "COMPLETED"

    # ---------------- EVALUATE ---------------- #

    def evaluate_interview(self, session_id: int):
        session = self.db.get(InterviewSession, session_id)

        if not session or session.status != "COMPLETED":
            raise HTTPException(400, "Interview not completed")

        qa = (
            self.db.query(InterviewQuestion, InterviewAnswer)
            .join(InterviewAnswer)
            .filter(InterviewQuestion.session_id == session.id)
            .order_by(InterviewQuestion.question_index)
            .all()
        )

        qa_data = [
            {"question": q.question_text, "answer": a.answer_text} for q, a in qa
        ]

        result = self.agent.evaluate_answers(qa_data)

        evaluation = InterviewEvaluation(
            session_id=session.id,
            total_score=result.total_score,
            feedback=result.overall_feedback,
        )

        self.db.add(evaluation)
        self.db.commit()

        return result

    # ---------------- INTERNAL ---------------- #

    def _get_active_session(self, session_id: int) -> InterviewSession:
        session = self.db.get(InterviewSession, session_id)

        if not session or session.status != "IN_PROGRESS":
            raise HTTPException(404, "Session not active")

        return session
