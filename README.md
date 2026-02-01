# Nagrik Sahayak – AI Powered Citizen Complaint Portal

## Problem
Citizens often face difficulty reporting civic issues, lack of transparency, and delayed responses.

## Solution
Nagrik Sahayak is a web-based platform that allows citizens to:
- File complaints using text, image, or voice
- Automatically summarize and classify complaints using AI
- Track complaint status via dashboard & history

## Tech Stack
Frontend: HTML, JavaScript, Bootstrap  
Backend: FastAPI (Python)  
Database: SQLite  
AI: Google Gemini API  
Email: SendGrid  

## Key Features
- AI-based complaint summarization
- Image-based issue verification
- Voice-to-text complaint filing
- Real-time dashboard & complaint history
- Email notifications

## Live Demo
Frontend: https://your-netlify-link  
Backend API: https://your-railway-link/docs

## How to Run Locally
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
