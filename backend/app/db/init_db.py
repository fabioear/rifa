import logging
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
from app.models.user import User
from app.core.security import get_password_hash
from app.models.tenant import Tenant
from app.core.config import settings

logger = logging.getLogger(__name__)

def init_db(db: Session) -> None:
    inspector = inspect(db.bind)
    cols = [c["name"] for c in inspector.get_columns("users")]
    if "phone" not in cols:
        db.execute(text("ALTER TABLE users ADD COLUMN phone VARCHAR NULL"))
        db.commit()
    if "whatsapp_opt_in" not in cols:
        db.execute(text("ALTER TABLE users ADD COLUMN whatsapp_opt_in BOOLEAN NOT NULL DEFAULT FALSE"))
        db.commit()
    # tenant = db.query(Tenant).filter(Tenant.domain == "localhost").first()
    # if not tenant:
    #     logger.info("Creating default localhost tenant...")
    #     tenant = Tenant(
    #         name="Localhost Dev",
    #         domain="localhost",
    #         primary_color="#4F46E5",
    #         secondary_color="#10B981"
    #     )
    #     db.add(tenant)
    #     db.commit()
    #     db.refresh(tenant)
    
    # 2. Create superuser if it doesn't exist
    # user = db.query(User).filter(User.email == "admin@example.com").first()
    # if not user:
    #     logger.info("Creating default admin user...")
    #     user = User(
    #         email="admin@example.com",
    #         password_hash=get_password_hash("admin"),
    #         is_active=True,
    #         role="admin",
    #         tenant_id=tenant.id
    #     )
    #     db.add(user)
    #     db.commit()
    #     db.refresh(user)
    #     logger.info("Default admin user created: admin@example.com / admin")
    # else:
    #     # Ensure admin belongs to localhost tenant
    #     if user.tenant_id != tenant.id:
    #         user.tenant_id = tenant.id
    #         db.commit()
    #         logger.info("Admin user linked to localhost tenant.")
    #     logger.info("Admin user already exists.")
