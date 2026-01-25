
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database.database import engine, Base
from backend.database import models # Import models to register them with Base
from dotenv import load_dotenv
import os

# Load .env from the same directory as this file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Create tables (simple auto-migration for now)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Autonomous Choice Learning Agent")

# CORS Setup
origins = [
    "http://localhost:5173", # Vite default
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.routers import auth, chat, goals, calendar, notifications, profile


app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(goals.router)
app.include_router(calendar.router)
app.include_router(notifications.router)
app.include_router(profile.router)

@app.get("/")
def read_root():
    return {"message": "Learning Agent Backend API is running."}

@app.get("/health")
def health_check():
    return {"status": "ok"}
