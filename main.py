from fastapi import FastAPI, File, UploadFile, HTTPException
import pdfplumber
import re
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000","http://10.246.238.129:3000"],  # Add both
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def extract_fields(text: str):
    # Regex for email & phone
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    phone_pattern = r"\+?\d[\d\-\s]{8,}\d"

    email = re.search(email_pattern, text)
    phone = re.search(phone_pattern, text)

    # For name: naive approach (first line of PDF text)
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    name = lines[0] if lines else None

    return {
        "name": name if name else "❌ Missing",
        "email": email.group(0) if email else "❌ Missing",
        "phone": phone.group(0) if phone else "❌ Missing",
    }


@app.post("/parse_resume/")
async def parse_resume(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        with pdfplumber.open(file.file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""

        if not text.strip():
            raise HTTPException(status_code=400, detail="No text found in PDF.")

        result = extract_fields(text)

        # Determine missing fields for frontend
        missing_fields = []
        if result["name"] == "❌ Missing":
            missing_fields.append("name")
        if result["email"] == "❌ Missing":
            missing_fields.append("email")
        if result["phone"] == "❌ Missing":
            missing_fields.append("phone")

        return {"success": True, "extracted": result, "missing_fields": missing_fields}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing PDF: {str(e)}")
