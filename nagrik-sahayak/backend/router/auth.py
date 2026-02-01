from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from database import SessionLocal
from models import User
from schemas import RegisterRequest, LoginRequest

router = APIRouter(prefix="/auth", tags=["Auth"])

# 🔒 USE PBKDF2 (NO WINDOWS ISSUES)
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)

# ---------------- DB ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------- PASSWORD ----------------
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)

# ---------------- REGISTER ----------------
@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.mobile == data.mobile).first():
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(
        name=data.name,
        mobile=data.mobile,
        password=hash_password(data.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "Registered successfully"}

# ---------------- LOGIN ----------------
@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.mobile == data.mobile).first()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # 🎯 UPDATED RETURN: Sending 'id' and 'token'
    return {
        "id": user.id,      
        "name": user.name,
        "mobile": user.mobile,
        "status": "success",
        "token": "session_token_123"
    }