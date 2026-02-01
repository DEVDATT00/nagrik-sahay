from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    mobile = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    language = Column(String, default="en")
    ai_updates = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    title = Column(String)
    description = Column(String)

    category = Column(String)          # NEW
    reference_id = Column(String)      # NEW (email ref id)

    status = Column(String, default="Pending")
    created_at = Column(DateTime, default=datetime.utcnow)
