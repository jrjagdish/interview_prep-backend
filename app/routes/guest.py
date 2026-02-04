from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Response, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.users import User
from app.services.uploadfile import upload_pdf_to_cloudinary
from app.utils.parser import parse_resume
from app.services.guestauthService import create_guest_user
from app.utils.security import verify_access_token
from app.core.config import settings

router = APIRouter(prefix="/guest", tags=["Guest Onboarding"])

@router.post("/register-with-resume")
async def register_guest_by_resume(
    response: Response,
    token: str = Query(..., description="The invite token from the admin link"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Onboards a candidate by parsing their resume and setting a guest cookie.
    Impact: Automates guest creation while linking them to the correct Admin.
    """
    # 1. Validate Invite Token and Admin Status
    admin_id = verify_access_token(token)
    
    # Check admin existence and status in one efficient query
    admin = db.query(User).filter(
        User.id == admin_id,
        User.role == "admin",
        User.is_active == True
    ).first()

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invite link is invalid or the admin account is no longer active."
        )

    # 2. Cloudinary Upload
    # Check file type before uploading to save Cloudinary bandwidth
    if not file.content_type == "application/pdf":
        raise HTTPException(400, "Only PDF resumes are supported.")

    upload_data = await upload_pdf_to_cloudinary(file)
    pdf_url = upload_data["url"]
    public_id = upload_data["public_id"]

    # 3. AI Resume Parsing
    resume_data = parse_resume(pdf_url)
    extracted = resume_data.get("extracted", {})
    email = extracted.get("email")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Could not extract email from resume. Please ensure it is visible."
        )

    # Determine username (AI name or fallback to email prefix)
    username = extracted.get("name") or email.split("@")[0]

    # 4. Create Guest & Set HttpOnly Cookie
    # The service now handles response.set_cookie internally
    guest_result = create_guest_user(
        username=username,
        email=email,
        admin_id=admin_id,
        pdf_url=pdf_url,
        cloudinary_public_id=public_id,
        response=response,
        db=db,
    )

    return {
        "success": True,
        "message": "Resume processed and guest session started.",
        "candidate": guest_result,
        "parsed_skills": extracted.get("skills", []),
        "interview_ready": True
    }