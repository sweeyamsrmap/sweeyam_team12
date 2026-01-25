import sqlite3
import os

db_path = "app.db"

if not os.path.exists(db_path):
    print(f"Error: {db_path} not found.")
    exit(1)

connection = sqlite3.connect(db_path)
cursor = connection.cursor()

try:
    print("Creating calendar_events and notifications tables...")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS calendar_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER REFERENCES users(id),
        goal_id INTEGER REFERENCES goals(id),
        title TEXT NOT NULL,
        description TEXT,
        start_time DATETIME NOT NULL,
        end_time DATETIME NOT NULL,
        is_completed BOOLEAN DEFAULT 0
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER REFERENCES users(id),
        title TEXT NOT NULL,
        message TEXT,
        type TEXT,
        is_read BOOLEAN DEFAULT 0,
        created_at DATETIME NOT NULL,
        scheduled_for DATETIME
    )
    """)
    
    connection.commit()
    print("Migration successful.")
except Exception as e:
    print(f"Migration failed: {e}")
    connection.rollback()
finally:
    connection.close()
