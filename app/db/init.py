from app.db.session import engine
from app.db.base import Base
from app.models.users import User,GuestUser
from app.models.interviewanswer import InterviewAnswer
from app.models.interviewevaluation import InterviewEvaluation
from app.models.interviewquestion import InterviewQuestion
from app.models.interviewsession import InterviewSession

def init_db():
    
    Base.metadata.create_all(bind=engine)
    
