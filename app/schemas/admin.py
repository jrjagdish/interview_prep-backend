# app/schemas/admin.py
from pydantic import BaseModel
from uuid import UUID

class GuestCandidateOut(BaseModel):
    id: UUID
    username: str
    email: str

    class Config:
        from_attributes = True

# app/schemas/admin.py
class AdminSessionScoreOut(BaseModel):
    session_id: int
    guest_username: str
    guest_email: str
    total_score: int
    max_score: int
    feedback: str | None

    class Config:
        from_attributes = True

