"""
Smart Attendance System — FastAPI Backend
Run with: uvicorn main:app --host 0.0.0.0 --port 8001 --reload
"""
import os, sys, logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

sys.path.insert(0, os.path.dirname(__file__))

from database import engine
import models
from routers import students as employees_router, attendance, recognition

# Auto-create all tables (drops nothing if already existing)
models.Base.metadata.create_all(bind=engine)

os.makedirs(os.path.join(os.path.dirname(__file__), "face_db"), exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Smart Employee Attendance System API",
    description="AI-powered face-recognition based attendance tracking for employees",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

face_db_path = os.path.join(os.path.dirname(__file__), "face_db")
app.mount("/face_images", StaticFiles(directory=face_db_path), name="face_images")

# /api/employees  →  employee CRUD + register
app.include_router(employees_router.router, prefix="/api/employees", tags=["Employees"])
# /api/attendance →  attendance records
app.include_router(attendance.router,       prefix="/api/attendance", tags=["Attendance"])
# /api/recognize  →  face recognition
app.include_router(recognition.router,      prefix="/api",            tags=["Recognition"])


@app.get("/", tags=["Health"])
def root():
    return {
        "message": "Smart Employee Attendance System API 🚀",
        "version": "2.0.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
