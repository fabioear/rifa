import sys
import os
# Ensure the parent directory is in python path to allow importing 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.tenant import Tenant
from app.models.user import User
from app.core.security import get_password_hash

def setup():
    db = SessionLocal()
    try:
        domain = "imperiodasrifas.app.br"
        tenant = db.query(Tenant).filter(Tenant.domain == domain).first()
        if not tenant:
            print(f"Creating tenant for {domain}...")
            tenant = Tenant(
                name="Imperio das Rifas",
                domain=domain,
                primary_color="#000000",
                secondary_color="#ffffff"
            )
            db.add(tenant)
            db.commit()
            db.refresh(tenant)
            print(f"Tenant created: {tenant.id}")
        else:
            print(f"Tenant {domain} already exists.")

        email = "admin@imperiodasrifas.app.br"
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"Creating user {email}...")
            user = User(
                email=email,
                password_hash=get_password_hash("admin123"),
                is_active=True,
                role="admin",
                tenant_id=tenant.id
            )
            db.add(user)
            db.commit()
            print(f"User created: {email} / admin123")
        else:
            print(f"User {email} already exists.")
            # Ensure tenant link
            if user.tenant_id != tenant.id:
                user.tenant_id = tenant.id
                db.commit()
                print(f"Updated user {email} to tenant {tenant.id}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    setup()
