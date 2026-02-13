import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
# Import models to ensure they are registered
from app.models.tenant import Tenant
from app.models.user import User
from app.models.rifa import Rifa
from app.models.rifa_numero import RifaNumero
from app.models.admin_settings import AdminSettings

def update_phones():
    db = SessionLocal()
    try:
        # Update all users
        # phone format: 5591984592434 (Standard BR format for API)
        new_phone = "5591984592434"
        
        # Execute update
        result = db.query(User).update({User.phone: new_phone})
        db.commit()
        
        print(f"Updated {result} users to phone {new_phone}")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_phones()
