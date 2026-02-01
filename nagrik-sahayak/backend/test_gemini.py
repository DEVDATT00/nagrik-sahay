import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("models/gemini-flash-latest")

res = model.generate_content("Translate this to English: सड़क पर गड्ढा है")
print(res.text)
