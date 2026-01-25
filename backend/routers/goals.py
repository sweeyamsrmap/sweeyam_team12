from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database.database import get_db
from backend.database.models import User, Goal
from backend.auth.dependencies import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/goals", tags=["goals"])

class GoalCreate(BaseModel):
    text: str
    deadline: str

class GoalResponse(BaseModel):
    id: int
    session_id: Optional[int] = None
    text: str
    deadline: Optional[str] = None
    status: str
    progress: int
    total_tasks: int
    completed_tasks: int
    
    class Config:
        from_attributes = True

@router.post("/", response_model=GoalResponse)
def create_goal(goal: GoalCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_goal = Goal(text=goal.text, deadline=goal.deadline, user_id=current_user.id)
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal

@router.get("/", response_model=List[GoalResponse])
def get_goals(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return current_user.goals
