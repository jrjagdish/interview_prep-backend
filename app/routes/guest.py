from fastapi import APIRouter, Depends, HTTPException, status , UploadFile, File
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.uploadfile import upload_pdf_to_cloudinary
from app.utils.parser import parse_resume
from app.services.guestauthService import create_guest_user

router = APIRouter(prefix="/guest", tags=["guest"])

@router.post("/upload_resume")
async def upload_resume( file: UploadFile = File(...), db: Session = Depends(get_db)):
    pdf_url = await upload_pdf_to_cloudinary(file)
    resume_data = parse_resume(pdf_url)
    if not resume_data.get("email"):
        raise HTTPException(
            status_code=400,
            detail="Email not found in resume",
        )
    username = resume_data.get("name") or resume_data["email"].split("@")[0]
    guest_user = create_guest_user(
        username=username,
        email=resume_data["email"],
        pdf_url=pdf_url,
        db=db
    )
    return {
        "success": True,
        "guest_user": guest_user,
        "resume_data": resume_data
    }

   