from backend.database.database import SessionLocal
from backend.database.models import User

def list_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"Total users: {len(users)}")
        for u in users:
            print(f"ID: {u.id}, Name: {u.name}, Email: {u.email}")
    finally:
        db.close()

if __name__ == "__main__":
    list_users()
