import sys
import os

# Add the backend directory to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Import models to ensure they are registered in SQLAlchemy
from app.db.session import SessionLocal
from app.models.tenant import Tenant
from app.models.user import User
from app.models.rifa import Rifa
# Add other models if necessary, but Tenant is likely the missing one for User

def list_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print("Users found in database:")
        for user in users:
            print(f"ID: {user.id} | Email: {user.email} | Role: {user.role} | Active: {user.is_active}")
            
        if not users:
            print("No users found in the database.")
            
    except Exception as e:
        print(f"Error listing users: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    list_users()
