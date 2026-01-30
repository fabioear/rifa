import sys
import os

# Add the backend directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.session import SessionLocal
from app.models.user import User
from app.models.tenant import Tenant # Import Tenant to resolve relationship

db = SessionLocal()
wrong_user = db.query(User).filter(User.email == "admin@example.com").first()
if wrong_user:
    db.delete(wrong_user)
    db.commit()
    print("Deleted wrong admin user: admin@example.com")
else:
    print("User admin@example.com not found.")
db.close()
