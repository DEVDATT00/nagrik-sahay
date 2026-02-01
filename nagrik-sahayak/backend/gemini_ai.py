import os
import google.generativeai as genai

# ---------------- GEMINI CONFIG ----------------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 🔥 REQUIRED MODEL (as per your instruction)
model = genai.GenerativeModel("models/gemini-flash-latest")


def generate_final_complaint(data: dict) -> str:
    """
    🚨 THIS IS THE ONLY GEMINI CALL IN THE ENTIRE SYSTEM 🚨

    Called ONLY when:
    - Language selected
    - Location selected
    - Voice processed
    - Image approved OR image optional
    """

    prompt = f"""
You are an AI civic assistant working for an Indian municipal system.

Generate a professional, polite English civic complaint letter.

DETAILS:
- Area: {data['location']['area']}
- Issue Type: {data['issue_type']}
- Citizen Description: {data['translated_text']}
- Image Evidence: {data['image_status']}
- Urgency Level: {data.get('urgency', 'Normal')}

INSTRUCTIONS:
- Formal government letter format
- Clear subject line
- No markdown
- No emojis
- No explanations, only the complaint letter
"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        # 🧹 Safety cleanup (sometimes Gemini wraps output)
        if text.startswith("```"):
            text = text.replace("```", "").strip()

        if not text:
            raise ValueError("Empty response from Gemini")

        return text

    except Exception as e:
        # 🛡️ Hackathon-safe fallback
        print("❌ Gemini generation failed:", e)

        return f"""
To,
The Concerned Municipal Authority,

Subject: Civic issue reported in {data['location']['area']}

Respected Sir/Madam,

I would like to bring to your attention the following civic issue reported by a citizen.

Issue Type: {data['issue_type']}
Description: {data['translated_text']}
Location: {data['location']['area']}

I kindly request the concerned department to inspect the matter and take appropriate action at the earliest.

Thanking you.

Yours sincerely,
A Concerned Citizen
""".strip()
