from app.db.session import engine
from app.db.base import Base
from app.models.users import User,GuestUser,Profile
from app.models.interview import InterviewSession,InterviewQA

def init_db():

    Base.metadata.create_all(bind=engine)
    
    
