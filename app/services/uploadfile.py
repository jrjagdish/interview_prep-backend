
from app.core import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, UploadFile

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


async def upload_pdf_to_cloudinary(file: UploadFile) -> str:
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 5 MB")

    result = cloudinary.uploader.upload(
        contents,
        
        resource_type="raw",
        folder="resumes",
        format="pdf"
    )

    return {
        "url": result.get("secure_url"),
        "public_id": result.get("public_id")
    }
