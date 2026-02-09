from sqlalchemy import create_engine
import os
from app.core.config import settings


DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL, echo=False)
