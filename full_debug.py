from backend.database.database import SessionLocal
from backend.database.models import User, ChatSession, Chat

def full_debug():
    db = SessionLocal()
    try:
        print("--- ALL USERS ---")
        users = db.query(User).all()
        for u in users:
            print(f"User ID: {u.id}, Email: {u.email}, Name: {u.name}")
        
        print("\n--- ALL SESSIONS ---")
        sessions = db.query(ChatSession).all()
        for s in sessions:
            msg_count = db.query(Chat).filter(Chat.session_id == s.id).count()
            print(f"Session ID: {s.id}, User ID: {s.user_id}, Title: {s.title}, Messages: {msg_count}")
            
        print("\n--- ORPHAN MESSAGES (No Session ID) ---")
        orphans = db.query(Chat).filter(Chat.session_id == None).all()
        for o in orphans:
            print(f"Msg ID: {o.id}, User ID: {o.user_id}, Message: {o.message[:50]}...")
            
    finally:
        db.close()

if __name__ == "__main__":
    full_debug()
