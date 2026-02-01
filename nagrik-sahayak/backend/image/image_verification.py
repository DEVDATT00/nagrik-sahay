import os
import json
from google import genai
from PIL import Image

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def verify_issue(image_np):
    image = Image.fromarray(image_np)

    prompt = """
You are an AI system for Smart City civic issue detection.

Analyze the image carefully.

A civic issue includes:
- potholes, cracks, broken or uneven road surfaces
- water-filled depressions on roads
- garbage or waste on streets
- broken or non-working street lights

IMPORTANT:
- Even small potholes or partial road damage count as civic issues.
- Do NOT reject road damage images.

Respond with ONLY valid JSON (no explanation, no markdown):

{
  "is_issue": true or false,
  "confidence": number between 0 and 100
}
"""

    response = client.models.generate_content(
        model="models/gemini-flash-latest",
        contents=[prompt, image]
    )

    text = response.text.strip()

    # Clean common Gemini formatting
    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(text)
    except Exception as e:
        print("JSON parse error:", text)
        return {"is_issue": False, "confidence": 0}

    return result
