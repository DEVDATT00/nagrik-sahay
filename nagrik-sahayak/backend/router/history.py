from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
import models

router = APIRouter(prefix="/complaint/history", tags=["History"])

# DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/{user_id}")
def complaint_history(user_id: int, db: Session = Depends(get_db)):
    complaints = (
        db.query(models.Complaint)
        .filter(models.Complaint.user_id == user_id)
        .order_by(models.Complaint.created_at.desc())
        .all()
    )

    return complaints
