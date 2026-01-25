from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.database import get_db, SessionLocal
from backend.database.models import User, Chat, ChatSession, Goal
from backend.auth.dependencies import get_current_user
from backend.agent.brain import AgentBrain
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/chat", tags=["chat"])
agent_brain = AgentBrain()

class ChatSessionCreate(BaseModel):
    title: Optional[str] = "New Chat"

class ChatSessionUpdate(BaseModel):
    title: str

from datetime import datetime

class ChatSessionResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str
    session_id: int

@router.post("/sessions", response_model=ChatSessionResponse)
def create_session(session: ChatSessionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_session = ChatSession(user_id=current_user.id, title=session.title)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

@router.get("/sessions", response_model=List[ChatSessionResponse])
def get_sessions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(ChatSession).filter(ChatSession.user_id == current_user.id).order_by(ChatSession.created_at.desc()).all()

from fastapi.responses import StreamingResponse
import json

@router.post("/message")
def chat_message(request: ChatRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Verify session belongs to user
    session = db.query(ChatSession).filter(ChatSession.id == request.session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # 1. Save user message
    user_msg = Chat(user_id=current_user.id, session_id=session.id, message=request.message, role="user")
    db.add(user_msg)
    db.commit()
    
    async def event_generator():
        # Create a fresh DB session for the background generator
        # This ensures the session stays open throughout the stream
        gen_db = SessionLocal()
        try:
            # Re-fetch objects to ensure they are bound to the new session
            gen_session = gen_db.query(ChatSession).filter(ChatSession.id == session.id).first()
            gen_user = gen_db.query(User).filter(User.id == current_user.id).first()
            
            full_agent_text = ""
            last_type = "chat"
            last_content = None
            
            async for chunk_str in agent_brain.process_message_stream(request.message, gen_user, gen_db, gen_session.id):
                chunk = json.loads(chunk_str.strip())
                
                if chunk["type"] == "chat_chunk":
                    full_agent_text += chunk["text"]
                elif chunk["type"] in ["plan", "resources"]:
                    last_type = chunk["type"]
                    last_content = json.dumps(chunk["content"]) if isinstance(chunk["content"], (dict, list)) else chunk["content"]
                elif chunk["type"] == "chat_end" and "full_text" in chunk:
                    full_agent_text = chunk["full_text"]
                    
                yield chunk_str

            # After stream finishes, save agent response to DB
            agent_msg = Chat(
                user_id=gen_user.id, 
                session_id=gen_session.id, 
                message=full_agent_text, 
                role="agent",
                msg_type=last_type,
                content=last_content
            )
            gen_db.add(agent_msg)
            
            # If it was a plan, also create/update a Goal
            if last_type == "plan" and last_content:
                try:
                    plan_data = json.loads(last_content)
                    goal_text = plan_data.get("overview", request.message)
                    if len(goal_text) > 150: goal_text = goal_text[:147] + "..."
                    
                    # Count total tasks in the weekly schedule
                    total_tasks = 0
                    for week in plan_data.get("weekly_schedule", []):
                        total_tasks += len(week.get("activities", []))
                    
                    # Attempt to extract duration/deadline from the plan or content
                    deadline_text = "2 weeks" # fallback
                    if "duration" in plan_data:
                        deadline_text = str(plan_data["duration"])
                    elif "timeframe" in plan_data:
                        deadline_text = str(plan_data["timeframe"])
                    elif "weekly_schedule" in plan_data:
                        weeks = len(plan_data["weekly_schedule"])
                        deadline_text = f"{weeks} weeks"

                    # Check if a goal already exists for this session
                    existing_goal = gen_db.query(Goal).filter(Goal.session_id == gen_session.id).first()
                    
                    if existing_goal:
                        existing_goal.text = goal_text
                        existing_goal.total_tasks = total_tasks
                        existing_goal.deadline = deadline_text
                        # Keep current progress/completed tasks unless reset is desired
                    else:
                        new_goal = Goal(
                            user_id=gen_user.id,
                            session_id=gen_session.id,
                            text=goal_text,
                            deadline=deadline_text, 
                            status="active",
                            total_tasks=total_tasks,
                            completed_tasks=0,
                            progress=0
                        )
                        gen_db.add(new_goal)
                except Exception as e:
                    print(f"Error saving goal: {e}")
            
            if gen_session.title == "New Chat":
                new_title = " ".join(request.message.split()[:5])
                gen_session.title = new_title
                
            gen_db.commit()
        except Exception as e:
            print(f"Error in event_generator: {e}")
            gen_db.rollback()
        finally:
            gen_db.close()

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")

@router.get("/history/{session_id}")
def get_chat_history(session_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    return db.query(Chat).filter(Chat.session_id == session_id).order_by(Chat.timestamp).all()

@router.patch("/sessions/{session_id}", response_model=ChatSessionResponse)
def update_session(session_id: int, update_data: ChatSessionUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    db_session.title = update_data.title
    db.commit()
    db.refresh(db_session)
    return db_session

@router.delete("/sessions/{session_id}")
def delete_session(session_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    db.delete(db_session)
    db.commit()
    return {"message": "Session deleted successfully"}
