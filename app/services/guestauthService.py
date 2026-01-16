from app.models.users import GuestUser
from fastapi import HTTPException, status,Depends
from sqlalchemy.orm import Session
from app.db.session import get_db

def create_guest_user(username: str, email: str, pdf_url: str, db: Session = Depends(get_db)):
    existing_user = db.query(GuestUser).filter(
        (GuestUser.username == username) | (GuestUser.email == email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Guest user with this username or email already exists."
        )
    guest_user = GuestUser(
        username=username,
        email=email,
        pdf_url=pdf_url
    )
    db.add(guest_user)
    db.commit()
    db.refresh(guest_user)
    return guest_user