import sqlite3
import os

db_path = "app.db"

if not os.path.exists(db_path):
    print(f"Error: {db_path} not found.")
    exit(1)

connection = sqlite3.connect(db_path)
cursor = connection.cursor()

try:
    print("Dropping goal_tasks table...")
    cursor.execute("DROP TABLE IF EXISTS goal_tasks")
    connection.commit()
    print("Drop table successful.")
except Exception as e:
    print(f"Drop table failed: {e}")
    connection.rollback()
finally:
    connection.close()
