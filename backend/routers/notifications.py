from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database.database import get_db
from backend.database.models import User, Notification
from backend.auth.dependencies import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/notifications", tags=["notifications"])

class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime
    scheduled_for: Optional[datetime] = None
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[NotificationResponse])
def get_notifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Fetch notifications that are either past their scheduled time or have no scheduled time
    now = datetime.now()
    return db.query(Notification).filter(
        Notification.user_id == current_user.id,
        (Notification.scheduled_for == None) | (Notification.scheduled_for <= now)
    ).order_by(Notification.created_at.desc()).all()

@router.patch("/{notification_id}/read")
def mark_read(notification_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    note = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Notification not found")
    note.is_read = True
    db.commit()
    return {"message": "Notification marked as read"}

@router.delete("/{notification_id}")
def delete_notification(notification_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    note = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Notification not found")
    db.delete(note)
    db.commit()
    return {"message": "Notification deleted"}
