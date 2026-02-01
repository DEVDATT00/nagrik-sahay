from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models import User
from schemas import (
    UserResponse,
    UpdateProfileRequest,
    UpdatePreferencesRequest
)

router = APIRouter(prefix="/user", tags=["User"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "fullName": user.name,
        "phone": user.mobile,
        "language": user.language,
        "ai_updates": user.ai_updates,
        "created_at": user.created_at.isoformat()
    }

@router.put("/{user_id}/profile")
def update_profile(
    user_id: int,
    data: UpdateProfileRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.name = data.fullName
    db.commit()

    return {"message": "Profile updated"}

@router.put("/{user_id}/preferences")
def update_preferences(
    user_id: int,
    data: UpdatePreferencesRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.language = data.language
    user.ai_updates = data.ai_updates
    db.commit()

    return {"message": "Preferences updated"}
