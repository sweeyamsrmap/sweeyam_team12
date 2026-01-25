from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database.database import get_db
from backend.database.models import User, CalendarEvent
from backend.auth.dependencies import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/calendar", tags=["calendar"])

class EventResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    is_completed: bool
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[EventResponse])
def get_calendar(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(CalendarEvent).filter(CalendarEvent.user_id == current_user.id).order_by(CalendarEvent.start_time).all()

@router.patch("/{event_id}/complete")
def complete_event(event_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id, CalendarEvent.user_id == current_user.id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    event.is_completed = True
    db.commit()
    return {"message": "Event marked as completed"}
