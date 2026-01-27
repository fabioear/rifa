import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.session import engine
from app.db.base import Base
# Import all models
from app.models.user import User
from app.models.rifa import Rifa
from app.models.rifa_numero import RifaNumero
from app.models.admin_settings import AdminSettings
from app.models.audit_finance import PaymentLog, AuditLog
from app.models.tenant import Tenant
from app.models.antifraud import BlockedEntity

def reset():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Done.")

if __name__ == "__main__":
    reset()
