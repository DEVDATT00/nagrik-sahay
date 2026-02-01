from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, Complaint
from schemas import DashboardResponse, ComplaintOut, DashboardStats

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# ---------------- DB SESSION ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally: 
        db.close()

# ---------------- GET DASHBOARD DATA ----------------
@router.get("/{user_id}", response_model=DashboardResponse)
def get_dashboard(user_id: int, db: Session = Depends(get_db)):
    """
    Fetches user information, calculation of report statistics, 
    and the 3 most recent complaints for the dashboard.
    """
    
    # 1. Verify User Exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. Fetch all complaints for this user
    # We fetch all to calculate stats, but we will only return the latest 3
    complaints = db.query(Complaint).filter(
        Complaint.user_id == user_id
    ).order_by(Complaint.created_at.desc()).all()

    # 3. Calculate Stats
    total = len(complaints)
    in_progress = len([c for c in complaints if c.status == "In Progress"])
    resolved = len([c for c in complaints if c.status == "Resolved"])
    escalated = len([c for c in complaints if c.status == "Escalated"])

    # 4. Prepare response data
    return {
        "user_name": user.name,
        "complaints": [
            ComplaintOut(
                id=c.id,
                title=c.title,
                status=c.status,
                created_at=c.created_at # Ensure this is in your ComplaintOut schema
            ) for c in complaints[:3]  # Return only the 3 most recent
        ],
        "stats": DashboardStats(
            total=total,
            in_progress=in_progress,
            resolved=resolved,
            escalated=escalated
        )
    }