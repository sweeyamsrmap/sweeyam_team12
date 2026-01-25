from backend.database.database import engine
from backend.database.models import Base

def migrate():
    print("Migrating: Creating goal_tasks table if it doesn't exist...")
    Base.metadata.create_all(bind=engine)
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
