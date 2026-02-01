from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base

from router.auth import router as auth_router
from router.user import router as user_router
from router.complaint import router as complaint_router
from router.history import router as history_router
from router.dashboard import router as dashboard_router   # ✅ ADD THIS

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(complaint_router)
app.include_router(history_router)
app.include_router(dashboard_router)   # ✅ ADD THIS

@app.get("/")
def root():
    return {"status": "Nagrik Sahayak Backend is running"}
