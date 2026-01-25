from backend.database.database import SessionLocal
from backend.database.models import ChatSession, Chat

def cleanup_sessions():
    db = SessionLocal()
    try:
        sessions = db.query(ChatSession).all()
        deleted_count = 0
        for s in sessions:
            msg_count = db.query(Chat).filter(Chat.session_id == s.id).count()
            if msg_count == 0:
                print(f"Deleting empty session {s.id}: {s.title}")
                db.delete(s)
                deleted_count += 1
        db.commit()
        print(f"Cleanup finished. Deleted {deleted_count} empty sessions.")
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_sessions()
