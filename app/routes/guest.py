from uuid import UUID
from fastapi import APIRouter, Depends, Form, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.users import User
from app.services.uploadfile import upload_pdf_to_cloudinary
from app.utils.parser import parse_resume
from app.services.guestauthService import create_guest_user
from app.utils.security import decode_invite_token


router = APIRouter(prefix="/guest", tags=["guest"])


@router.post("/upload_resume")
async def upload_resume(
    token: str = Query(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    admin_id = decode_invite_token(token)

    admin = (
        db.query(User)
        .filter(
            User.id == admin_id,
            User.role == "admin",
            User.is_active == True,
        )
        .first()
    )

    if not admin:
        raise HTTPException(status_code=404, detail="Invalid invite link")

    upload_data = await upload_pdf_to_cloudinary(file)
    pdf_url = upload_data["url"]
    public_id = upload_data["public_id"]

    resume_data = parse_resume(pdf_url)
    email = resume_data["extracted"].get("email")

    if not email:
        raise HTTPException(status_code=400, detail="Email not found in resume")

    username = (
        resume_data["extracted"].get("name")
        or email.split("@")[0]
    )

    guest_user, access_token = create_guest_user(
        username=username,
        email=email,
        admin_id=admin_id,
        pdf_url=pdf_url,
        cloudinary_public_id=public_id,
        db=db,
    )

    return {
        "success": True,
        "guest_user": {
            "id": guest_user.id,
            "username": guest_user.username,
            "email": guest_user.email,
        },
        "resume_data": resume_data,
        "access_token": access_token,
    }
