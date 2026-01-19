from uuid import UUID
from app.models.users import GuestUser
from fastapi import HTTPException, status,Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.utils.security import create_guest_token

def create_guest_user(username: str, email: str, pdf_url: str,cloudinary_public_id: str,admin_id: UUID, db: Session = Depends(get_db)):
    existing_user = db.query(GuestUser).filter(
        GuestUser.email == email
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Guest user with this username or email already exists."
        )
    guest_user = GuestUser(
        username=username,
        email=email,
        pdf_url=pdf_url,
        cloudinary_public_id = cloudinary_public_id,
        admin_id=admin_id,
    )
    db.add(guest_user)
    db.commit()
    db.refresh(guest_user)
    token = create_guest_token(guest_id=str(guest_user.id))
    return guest_user,token