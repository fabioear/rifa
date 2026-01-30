import sys
import os

# Add the backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.models.user import User
from app.models.tenant import Tenant
# Import all models to resolve relationships
from app.models import rifa, rifa_numero, tenant
from app.core.security import get_password_hash

def create_first_user():
    db = SessionLocal()
    try:
        # 1. Create default tenant if not exists
        tenant = db.query(Tenant).filter(Tenant.domain == "localhost").first()
        if not tenant:
            print("Creating default localhost tenant...")
            tenant = Tenant(
                name="Localhost Dev",
                domain="localhost",
                primary_color="#4F46E5",
                secondary_color="#10B981"
            )
            db.add(tenant)
            db.commit()
            db.refresh(tenant)
        
        email = "suporte@imperiodasrifas.app.br"
        password = "Admin123"
        
        # Check if exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"User {email} already exists.")
            return

        user = User(
            email=email,
            password_hash=get_password_hash(password),
            is_active=True,
            role="admin",
            tenant_id=tenant.id
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
