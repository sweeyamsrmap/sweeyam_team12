from backend.database.database import engine
from sqlalchemy import inspect

def verify():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("Tables in database:", tables)
    if "goal_tasks" in tables:
        print("✅ goal_tasks table exists!")
        columns = [c['name'] for c in inspector.get_columns("goal_tasks")]
        print("Columns in goal_tasks:", columns)
    else:
        print("❌ goal_tasks table NOT found!")

if __name__ == "__main__":
    verify()
