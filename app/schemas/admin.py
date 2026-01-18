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
    guest_username: str | None
    guest_email: str | None
    total_score: float
    already_evaluated: bool = False

    class Config:
        from_attributes = True

