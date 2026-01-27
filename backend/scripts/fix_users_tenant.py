import sys
import os

# Add the parent directory to sys.path to allow importing app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.user import User
from app.models.tenant import Tenant

def fix_users_tenant():
    db = SessionLocal()
    try:
        # Get the localhost tenant
        tenant = db.query(Tenant).filter(Tenant.domain == "localhost").first()
        if not tenant:
            print("Tenant 'localhost' not found.")
            return

        print(f"Using tenant: {tenant.name} ({tenant.id})")

        # Find users with NULL tenant_id
        users = db.query(User).filter(User.tenant_id == None).all()
        
        count = 0
        for user in users:
            print(f"Fixing user: {user.email}")
            user.tenant_id = tenant.id
            count += 1
            
        if count > 0:
            db.commit()
            print(f"Successfully fixed {count} users.")
        else:
            print("No users found with NULL tenant_id.")
            
    except Exception as e:
        print(f"Error fixing users: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_users_tenant()
