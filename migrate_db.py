import sqlite3
import os

db_path = "app.db"

if not os.path.exists(db_path):
    print(f"Error: {db_path} not found.")
    exit(1)

connection = sqlite3.connect(db_path)
cursor = connection.cursor()

try:
    print("Migrating database...")
    # Add msg_type column
    try:
        cursor.execute("ALTER TABLE chats ADD COLUMN msg_type TEXT DEFAULT 'chat'")
        print("Added column msg_type to chats table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("Column msg_type already exists.")
        else:
            raise e

    # Add content column
    try:
        cursor.execute("ALTER TABLE chats ADD COLUMN content TEXT")
        print("Added column content to chats table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("Column content already exists.")
        else:
            raise e

    connection.commit()
    print("Migration successful.")
except Exception as e:
    print(f"Migration failed: {e}")
    connection.rollback()
finally:
    connection.close()
