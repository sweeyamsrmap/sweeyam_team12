import sqlite3
import os

db_path = "app.db"

if not os.path.exists(db_path):
    print(f"Error: {db_path} not found.")
    exit(1)

connection = sqlite3.connect(db_path)
cursor = connection.cursor()

try:
    print("Migrating goals table...")
    # Add session_id column
    try:
        cursor.execute("ALTER TABLE goals ADD COLUMN session_id INTEGER REFERENCES chat_sessions(id)")
        print("Added column session_id to goals table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("Column session_id already exists.")
        else:
            raise e

    connection.commit()
    print("Migration successful.")
except Exception as e:
    print(f"Migration failed: {e}")
    connection.rollback()
finally:
    connection.close()
