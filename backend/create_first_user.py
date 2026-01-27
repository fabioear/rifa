import sys
import os

# Add the backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.models.user import User
# Import all models to resolve relationships
from app.models import rifa, rifa_numero
from app.core.security import get_password_hash

def create_first_user():
    db = SessionLocal()
    try:
        email = "admin@example.com"
        password = "admin"
        
        # Check if exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"User {email} already exists.")
            return

        user = User(
            email=email,
            password_hash=get_password_hash(password),
            is_active=True,
            role="admin"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print("User created successfully!")
        print(f"Email: {email}")
        print(f"Password: {password}")
    except Exception as e:
        print(f"Error creating user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_first_user()
