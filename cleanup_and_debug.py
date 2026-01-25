from backend.database.database import SessionLocal
from backend.database.models import User, ChatSession, Chat

def cleanup_and_debug():
    db = SessionLocal()
    try:
        # 1. Cleanup test data
        test_queries = ["neon purple", "space rockets", "test_memory"]
        for q in test_queries:
            deleted = db.query(Chat).filter(Chat.message.like(f"%{q}%")).delete(synchronize_session=False)
            print(f"Deleted {deleted} test messages matching '{q}'")
        
        # 2. Check for User 1's sessions and messages
        user1_sessions = db.query(ChatSession).filter(ChatSession.user_id == 1).all()
        print(f"\nUser 1 has {len(user1_sessions)} sessions")
        for s in user1_sessions:
            msgs = db.query(Chat).filter(Chat.session_id == s.id).all()
            print(f"  Session {s.id} ({s.title}): {len(msgs)} messages")
            if len(msgs) > 0:
                for m in msgs[:2]:
                    print(f"    [{m.role}] {m.message[:30]}...")

        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_and_debug()
