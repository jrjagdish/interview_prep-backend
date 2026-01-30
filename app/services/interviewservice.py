from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from app.ai.interviewagent import InterviewAgent
from app.models.interview import InterviewSession, InterviewQA
from app.core.config import settings

class InterviewService:
    def __init__(self, db: Session):
        self.db = db
        # Pass the API Key to the agent
        self.ai_agent = InterviewAgent(groq_api_key=settings.GROQ_API_KEY)
        self.MAX_QUESTIONS = 6

    def start_interview_session(self, role: str, level: str, admin_id: UUID | None, user_id: UUID | None, guest_id: UUID | None):
        if user_id is None and guest_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Identity missing.")

        # 1. Create Session first
        title = f"{level.capitalize()} {role.capitalize()} Mock Interview"
        session = InterviewSession(
            user_id=user_id,
            guest_user_id=guest_id,
            admin_id=admin_id,
            title=title,
            current_question_index=0,
            status="IN_PROGRESS"
        )
        self.db.add(session)
        self.db.flush() # Get session.id

        # 2. Generate ONLY the first question
        questions = self.ai_agent.generate_questions(count=1, level=level, role=role)
        first_q = questions[0] if questions else "Can you tell me about your experience?"

        # 3. Save first QA
        qa_entry = InterviewQA(
            session_id=session.id, 
            question_text=first_q, 
            question_index=0
        )
        self.db.add(qa_entry)
        self.db.commit()

        return {"session_id": session.id, "title": session.title, "question": first_q}

    def submit_answer(self, session_id: UUID, answer: str):
        session = self.db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
        if not session or session.status == "COMPLETED":
            raise HTTPException(status_code=400, detail="Session inactive.")

        # 1. Get current QA record
        qa_entry = self.db.query(InterviewQA).filter(
            InterviewQA.session_id == session_id,
            InterviewQA.question_index == session.current_question_index
        ).first()

        if not qa_entry: raise HTTPException(404, "Question not found")

        # 2. Get AI Feedback for the CURRENT answer
        # We pass the single Q&A to the evaluation tool
        eval_result = self.ai_agent.evaluate_single_answer(qa_entry.question_text, answer)
        
        qa_entry.user_answer = answer
        qa_entry.ai_feedback = eval_result.feedback
        qa_entry.score = eval_result.score
        
        # 3. Prepare for next step
        session.current_question_index += 1
        completed = session.current_question_index >= self.MAX_QUESTIONS

        next_question_text = None
        if not completed:
            # 4. Generate NEXT question based on previous context
            # Pass history so AI doesn't repeat itself
            history = [{"q": qa.question_text, "a": qa.user_answer} for qa in session.qa_history if qa.user_answer]
            next_q_list = self.ai_agent.generate_questions(
                count=1, level=session.title, role="", history=history
            )
            next_question_text = next_q_list[0]

            # Save the next question to DB
            next_qa = InterviewQA(
                session_id=session.id,
                question_text=next_question_text,
                question_index=session.current_question_index
            )
            self.db.add(next_qa)
        else:
            session.status = "COMPLETED"

        self.db.commit()

        return {
            "ai_feedback": qa_entry.ai_feedback,
            "score": qa_entry.score,
            "next_question": next_question_text,
            "completed": completed
        }