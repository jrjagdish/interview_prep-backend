from fastapi import HTTPException
import pdfplumber
import re
from io import BytesIO
import requests


def extract_fields(text: str):
    # Your existing function...
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    phone_pattern = r"\+?\d[\d\-\s]{8,}\d"

    email = re.search(email_pattern, text)
    phone = re.search(phone_pattern, text)

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    name = lines[0] if lines else None

    return {
        "name": name if name else "❌ Missing",
        "email": email.group(0) if email else "❌ Missing",
        "phone": phone.group(0) if phone else "❌ Missing",
    }


MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def download_pdf_from_url(url: str) -> BytesIO:
    response = requests.get(
        url,
        stream=True,
        timeout=10,
    )
    response.raise_for_status()
    content = BytesIO()
    total_size = 0
    for chunk in response.iter_content(chunk_size=8192):
        total_size += len(chunk)
        if total_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400, detail="File size exceeds the 5 MB limit."
            )
        content.write(chunk)
    content.seek(0)
    return content


async def parse_resume(pdf_url: str):

    if not pdf_url.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        file = download_pdf_from_url(pdf_url)
        text = ""
        with pdfplumber.open(file) as pdf:

            for page in pdf.pages:
                text += page.extract_text() or ""

        if not text.strip():
            raise HTTPException(status_code=400, detail="No text found in PDF.")

        result = extract_fields(text)

        missing_fields = [
            field for field, value in result.items() if value == "❌ Missing"
        ]

        return {"success": True, "extracted": result, "missing_fields": missing_fields}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing PDF: {str(e)}")
