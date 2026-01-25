from backend.database.database import SessionLocal
from backend.database.models import User, ChatSession, Chat

def debug_db():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        for u in users:
            print(f"\nUser: {u.id} ({u.email})")
            sessions = db.query(ChatSession).filter(ChatSession.user_id == u.id).all()
            print(f"  Sessions: {len(sessions)}")
            for s in sessions:
                messages = db.query(Chat).filter(Chat.session_id == s.id).all()
                print(f"    Session {s.id} ({s.title}): {len(messages)} messages")
                for m in messages:
                    print(f"      [{m.role}] {m.message[:50]}...")
    finally:
        db.close()

if __name__ == "__main__":
    debug_db()
