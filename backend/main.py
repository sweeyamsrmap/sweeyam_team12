from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load .env FIRST
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

# Import DB after env is loaded
from backend.database.database import engine, Base
from backend.database import models  # registers models

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Autonomous Choice Learning Agent")

# CORS Setup (OK for local dev)
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://qubex-frontend.vercel.app/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
from backend.routers import auth, chat, goals, calendar, notifications, profile

app.include_router(auth.router, prefix="/auth")
app.include_router(chat.router, prefix="/chat")
app.include_router(goals.router, prefix="/goals")
app.include_router(calendar.router, prefix="/calendar")
app.include_router(notifications.router, prefix="/notifications")
app.include_router(profile.router, prefix="/profile")

@app.get("/")
def read_root():
    return {"message": "Learning Agent Backend API is running."}

@app.get("/health")
def health_check():
    return {"status": "ok"}
