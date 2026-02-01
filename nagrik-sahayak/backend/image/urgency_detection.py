import os
from google import genai
from PIL import Image

# Create Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def determine_urgency(image_np, issue_type):
    """
    Determines urgency of the civic issue.
    Returns one of:
    Low / Medium / High
    """

    # Convert numpy array to PIL Image
    image = Image.fromarray(image_np)

    prompt = f"""
    You are an AI assistant responsible for prioritizing civic issues.

The issue type is: {issue_type}

Determine urgency based on:
- Size and severity of the issue
- Risk to pedestrians, vehicles, or public safety
- Area affected (small/local vs widespread)

Urgency rules:
- HIGH:
  • Large potholes
  • Deep road damage
  • Garbage covering a large area
  • Street lights broken in busy or dark areas
- MEDIUM:
  • Moderate damage
  • Issues that are noticeable but not immediately dangerous
- LOW:
  • Minor issues
  • Small cracks or limited garbage

Respond with ONLY ONE word:
- Low
- Medium
- High

    """

    response = client.models.generate_content(
        model="models/gemini-flash-lite-latest",
        contents=[prompt, image]
    )

    return response.text.strip()
