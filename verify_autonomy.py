import sqlite3
from datetime import datetime, timedelta

def verify_autonomy():
    db_path = "app.db"
    # Ensure DB is closed and accessible
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 1. Test Notification Creation
        print("Testing Notification persistence...")
        now = datetime.now()
        # Ensure at least one user exists
        cursor.execute("SELECT id FROM users LIMIT 1")
        user = cursor.fetchone()
        if not user:
            print("No users found. Creating dummy user...")
            cursor.execute("INSERT INTO users (name, email) VALUES ('Test User', 'test@example.com')")
            user_id = cursor.lastrowid
        else:
            user_id = user[0]

        cursor.execute("""
            INSERT INTO notifications (user_id, title, message, type, created_at)
            VALUES (?, 'Test Notification', 'Autonomous agent check.', 'reminder', ?)
        """, (user_id, now.isoformat()))
        
        # 2. Test Calendar Event Creation
        print("Testing Calendar Event persistence...")
        start = (now + timedelta(hours=1)).isoformat()
        end = (now + timedelta(hours=2)).isoformat()
        cursor.execute("""
            INSERT INTO calendar_events (user_id, title, start_time, end_time)
            VALUES (?, 'Test Learning Session', ?, ?)
        """, (user_id, start, end))
        
        conn.commit()
        
        # Verification queries
        cursor.execute("SELECT COUNT(*) FROM notifications WHERE title = 'Test Notification'")
        notes_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM calendar_events WHERE title = 'Test Learning Session'")
        events_count = cursor.fetchone()[0]
        
        if notes_count > 0 and events_count > 0:
            print(f"✅ Autonomous features verified in DB: {notes_count} notifications, {events_count} events.")
        else:
            print("❌ Verification failed.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    verify_autonomy()
