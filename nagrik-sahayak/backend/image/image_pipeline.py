import os
import json
from google import genai
from PIL import Image

# ---------------- GEMINI CLIENT ----------------
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Image confidence threshold
CONFIDENCE_THRESHOLD = 70


def process_image(image_np):
    """
    STEP 5: Image Analysis ONLY

    - Detects civic issue from image
    - Extracts issue type, urgency, confidence
    - NEVER generates complaint
    - NEVER rejects citizen input
    """

    image = Image.fromarray(image_np)

    prompt = """
You are an AI system for Indian Smart City civic issue detection.

Analyze the image and return ALL of the following in ONE response:

1. Is this a real civic issue?
2. What is the issue type?
   - Pothole
   - Garbage
   - Street Light
   - Other
3. How urgent is it? (Low / Medium / High)
4. Confidence score (0–100)

IMPORTANT RULES:
- Even small potholes or cracks are valid civic issues.
- Do NOT reject clear road damage.
- If image is unclear, lower confidence instead of rejecting.

Respond ONLY in valid JSON:
{
  "is_issue": true or false,
  "issue_type": "Pothole | Garbage | Street Light | Other",
  "urgency": "Low | Medium | High",
  "confidence": number
}
"""

    try:
        response = client.models.generate_content(
            model="models/gemini-flash-lite-latest",
            contents=[prompt, image]
        )

        text = response.text.strip()

        # 🧹 Cleanup Gemini formatting
        if text.startswith("```"):
            text = text.replace("```json", "").replace("```", "").strip()

        result = json.loads(text)

    except Exception as e:
        print("❌ Image AI error:", e)
        return {
            "status": "error",
            "message": "Image analysis failed"
        }

    # 🟡 Low confidence or not an issue → image rejected (NOT voice)
    if not result.get("is_issue") or result.get("confidence", 0) < CONFIDENCE_THRESHOLD:
        return {
            "status": "rejected",
            "confidence": result.get("confidence", 0)
        }

    # 🟢 Image accepted
    return {
        "status": "accepted",
        "issue_type": result.get("issue_type", "Other"),
        "urgency": result.get("urgency", "Normal"),
        "confidence": result.get("confidence", 0)
    }
