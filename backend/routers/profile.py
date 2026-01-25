from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.database.models import User, Goal, ChatSession
from backend.auth.dependencies import get_current_user
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/profile", tags=["profile"])

class ProfileResponse(BaseModel):
    id: int
    name: str
    email: str
    username: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    
    class Config:
        from_attributes = True

class ProfileUpdate(BaseModel):
    username: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

class StatsResponse(BaseModel):
    total_goals: int
    active_goals: int
    completed_goals: int
    total_sessions: int
    total_progress: int  # Average progress across all goals

@router.get("/me", response_model=ProfileResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.patch("/me", response_model=ProfileResponse)
def update_profile(
    update: ProfileUpdate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    if update.username is not None:
        # Check if username is already taken by another user
        existing = db.query(User).filter(
            User.username == update.username, 
            User.id != current_user.id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")
        current_user.username = update.username
    
    if update.bio is not None:
        current_user.bio = update.bio
    
    if update.avatar_url is not None:
        current_user.avatar_url = update.avatar_url
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/stats", response_model=StatsResponse)
def get_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    goals = db.query(Goal).filter(Goal.user_id == current_user.id).all()
    sessions = db.query(ChatSession).filter(ChatSession.user_id == current_user.id).count()
    
    total_goals = len(goals)
    active_goals = len([g for g in goals if g.status == "active"])
    completed_goals = len([g for g in goals if g.status == "completed"])
    
    avg_progress = 0
    if total_goals > 0:
        avg_progress = sum(g.progress for g in goals) // total_goals
    
    return {
        "total_goals": total_goals,
        "active_goals": active_goals,
        "completed_goals": completed_goals,
        "total_sessions": sessions,
        "total_progress": avg_progress
    }
