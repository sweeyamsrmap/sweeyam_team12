from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime, timezone

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    username = Column(String, unique=True, index=True, nullable=True)  # Display name
    bio = Column(Text, nullable=True)  # User biography
    avatar_url = Column(String, nullable=True)  # Profile picture URL
    settings = Column(JSON, default=dict)  # User preferences as JSON
    
    chats = relationship("Chat", back_populates="user")
    goals = relationship("Goal", back_populates="user")
    plans = relationship("Plan", back_populates="user")
    preferences = relationship("Preference", back_populates="user", uselist=False)
    chat_sessions = relationship("ChatSession", back_populates="user")

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, default="New Chat")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("Chat", back_populates="session", cascade="all, delete-orphan")

class Chat(Base):
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text)
    role = Column(String)  # 'user' or 'agent'
    msg_type = Column(String, default="chat") # 'chat', 'plan', 'resources', 'error'
    content = Column(Text, nullable=True) # JSON string for extra content
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="chats")
    session = relationship("ChatSession", back_populates="messages")

class Goal(Base):
    __tablename__ = "goals"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=True)
    text = Column(String)
    deadline = Column(String)
    status = Column(String, default="active")
    progress = Column(Integer, default=0) # percentage
    total_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    
    user = relationship("User", back_populates="goals")
    session = relationship("ChatSession")

class Plan(Base):
    __tablename__ = "plans"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content_json = Column(Text) # JSON string
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="plans")

class Preference(Base):
    __tablename__ = "preferences"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    weak_topics = Column(String) # Comma separated or JSON
    strong_topics = Column(String)
    
    user = relationship("User", back_populates="preferences")

class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=True)
    title = Column(String)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    is_completed = Column(Boolean, default=False)
    
    user = relationship("User")
    goal = relationship("Goal")

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    message = Column(Text)
    type = Column(String)  # 'daily_task', 'reminder', 'system'
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    scheduled_for = Column(DateTime, nullable=True)
    
    user = relationship("User")
