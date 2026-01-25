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
    # Add progress column
    try:
        cursor.execute("ALTER TABLE goals ADD COLUMN progress INTEGER DEFAULT 0")
        print("Added column progress to goals table.")
    except sqlite3.OperationalError:
        print("Column progress already exists.")

    # Add total_tasks column
    try:
        cursor.execute("ALTER TABLE goals ADD COLUMN total_tasks INTEGER DEFAULT 0")
        print("Added column total_tasks to goals table.")
    except sqlite3.OperationalError:
        print("Column total_tasks already exists.")

    # Add completed_tasks column
    try:
        cursor.execute("ALTER TABLE goals ADD COLUMN completed_tasks INTEGER DEFAULT 0")
        print("Added column completed_tasks to goals table.")
    except sqlite3.OperationalError:
        print("Column completed_tasks already exists.")

    connection.commit()
    print("Migration successful.")
except Exception as e:
    print(f"Migration failed: {e}")
    connection.rollback()
finally:
    connection.close()
