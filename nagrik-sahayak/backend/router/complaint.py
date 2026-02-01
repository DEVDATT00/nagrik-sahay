from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from sqlalchemy.orm import Session
from database import SessionLocal
from voice_input import voice_to_text
from PIL import Image
import numpy as np
import io
import models
from fastapi.responses import FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import uuid
import os
from tempfile import NamedTemporaryFile
from sendgrid_submission import submit_via_email
from fastapi.responses import FileResponse
# Image pipeline
from image.image_pipeline import process_image

# Gemini (ONLY used in final step)
from gemini_ai import generate_final_complaint

router = APIRouter(prefix="/complaint", tags=["Complaint"])


# =====================================================
# 📄 DOWNLOAD PDF
# =====================================================


@router.post("/download-pdf")
async def download_pdf(request: Request):
    data = await request.json()
    complaint_text = data.get("complaint")

    if not complaint_text:
        raise HTTPException(status_code=400, detail="Complaint text missing")

    # ✅ Cross-platform temp file
    with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        file_path = tmp.name

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica", 11)

    x = 50
    y = height - 50

    for line in complaint_text.split("\n"):
        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 11)
            y = height - 50

        c.drawString(x, y, line)
        y -= 14

    c.save()

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename="Nagrik_Sahayak_Complaint.pdf"
    )


# ---------------- DB SESSION ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- HINDI → ENGLISH (SAFE FALLBACK) ----------------
def translate_hi_to_en_fallback(text: str) -> str:
    translations = {
        "सड़क": "road",
        "गड्ढा": "pothole",
        "बहुत": "very",
        "बड़ा": "large",
        "कचरा": "garbage",
        "पानी": "water",
        "लीक": "leak",
        "नाली": "drainage",
        "लाइट": "street light",
        "खराब": "damaged",
        "समस्या": "problem",
        "यहाँ": "here",
        "पर": "on",
        "है": "is"
    }

    translated = text.lower()
    for hi, en in translations.items():
        translated = translated.replace(hi, en)

    return translated


# ---------------- ISSUE EXTRACTION (NO AI) ----------------
def extract_issue_fallback(text: str) -> str:
    t = text.lower()

    if "pothole" in t:
        return "Pothole"
    if "garbage" in t:
        return "Garbage"
    if "water" in t or "leak" in t:
        return "Water Leakage"
    if "street light" in t or "lamp" in t:
        return "Street Light"
    if "drain" in t or "sewer" in t:
        return "Drainage"

    return "Other"


# ---------------- IMAGE REQUIRED RULE ----------------
def is_image_required(issue_type: str) -> bool:
    REQUIRED = [
        "Pothole",
        "Garbage",
        "Broken Road",
        "Open Manhole"
    ]
    return issue_type in REQUIRED


# ---------------- ISSUE MATCHING ----------------
def normalize(issue: str) -> str:
    return issue.lower().strip() if issue else ""


def is_issue_consistent(voice_issue: str, image_issue: str) -> bool:
    return normalize(voice_issue) == normalize(image_issue)


# =====================================================
# 🟢 STEP 3: VOICE ONLY
# =====================================================
@router.post("/trigger-mic")
async def trigger_mic(request: Request):
    try:
        body = await request.json()
        location = body.get("location")
        language = body.get("language", "hi-IN")
        image_analysis = body.get("image_analysis")

        if not location or not location.get("area"):
            return {"success": False, "error": "Location is mandatory"}

        raw_text = voice_to_text(language=language)

        if raw_text in ["Voice not understood", "Speech service not available"]:
            return {"success": False, "error": raw_text}

        if language.startswith("hi"):
            translated_text = translate_hi_to_en_fallback(raw_text)
        else:
            translated_text = raw_text

        issue_type = extract_issue_fallback(translated_text)

        if image_analysis:
            image_issue = image_analysis.get("issue_type")
            if image_issue and not is_issue_consistent(issue_type, image_issue):
                return {
                    "success": False,
                    "mismatch": True,
                    "voice_issue": issue_type,
                    "image_issue": image_issue,
                    "error": (
                        f"Your voice describes '{issue_type}', "
                        f"but the image shows '{image_issue}'. "
                        f"Please upload a relevant image."
                    )
                }

        return {
            "success": True,
            "raw_text": raw_text,
            "translated_text": translated_text,
            "issue_type": issue_type
        }

    except Exception as e:
        print("❌ trigger-mic error:", e)
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# 🟢 STEP 6: FINAL REPORT GENERATION (ONLY GEMINI CALL)
# =====================================================
@router.post("/final-generate")
async def final_generate(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()

        issue_type = data["issue_type"]
        translated_text = data["translated_text"]
        location = data["location"]
        image_analysis = data.get("image_analysis")

        if is_image_required(issue_type) and not image_analysis:
            return {
                "success": False,
                "error": "This issue requires a photo for verification"
            }

        image_status = (
            "Approved photographic evidence attached"
            if image_analysis else
            "Photographic evidence could not be provided due to the nature of the issue"
        )

        payload = {
            "translated_text": translated_text,
            "issue_type": issue_type,
            "location": location,
            "image_status": image_status,
            "urgency": image_analysis.get("urgency") if image_analysis else "Normal"
        }

        complaint_text = generate_final_complaint(payload)

        user_id = data.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="User not logged in")

        report = models.Complaint(
            user_id=user_id,
            title=f"{issue_type} issue in {location.get('area')}",
            description=complaint_text,
            category=issue_type
        )


        db.add(report)
        db.commit()
        db.refresh(report)

        return {
            "success": True,
            "complaint": complaint_text,
            "complaint_id": report.id   # ✅ correct, NOT reference_id
        }

    except Exception as e:
        print("❌ final-generate error:", e)
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# 🟢 IMAGE ANALYSIS
# =====================================================
@router.post("/analyze-image")
async def analyze_image(image: UploadFile = File(...)):
    try:
        contents = await image.read()
        pil_image = Image.open(io.BytesIO(contents)).convert("RGB")
        image_np = np.array(pil_image)

        result = process_image(image_np)

        if result.get("status") != "accepted":
            return {
                "success": False,
                "status": "rejected",
                "confidence": result.get("confidence", 0)
            }

        return {
            "success": True,
            "issue_type": result.get("issue_type"),
            "urgency": result.get("urgency", "Normal"),
            "confidence": result.get("confidence", 0)
        }

    except Exception as e:
        print("❌ image error:", e)
        return {
            "success": False,
            "status": "error",
            "message": str(e)
        }

@router.post("/submit-email")
async def submit_email(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()

        if not data.get("description"):
            return {"success": False, "error": "Report text missing"}

        # 1️⃣ Send email
        result = submit_via_email({
            "description": data["description"],
            "city": data.get("city", "Unknown"),
            "urgency": data.get("urgency", "Normal")
        })

        if result["status"] != "success":
            return {
                "success": False,
                "error": result["message"]
            }

        # 2️⃣ SAVE reference_id INTO DATABASE  ✅✅✅
        reference_id = result["reference_id"]

        complaint_id = data.get("complaint_id")
        if complaint_id:
            complaint = db.query(models.Complaint).filter(
                models.Complaint.id == complaint_id
            ).first()

            if complaint:
                complaint.reference_id = reference_id
                complaint.status = "Submitted"
                db.commit()

        # 3️⃣ Return response to frontend
        return {
            "success": True,
            "reference_id": reference_id
        }

    except Exception as e:
        print("❌ submit-email error:", e)
        raise HTTPException(status_code=500, detail=str(e))
