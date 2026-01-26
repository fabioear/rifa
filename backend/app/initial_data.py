import logging

from app.db.session import SessionLocal
from app.models.tenant import Tenant
from app.models.user import User, UserRole
from app.core.config import settings
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db(db: SessionLocal) -> None:
    # 1. Create Default Tenant
    tenant = db.query(Tenant).filter(Tenant.slug == "default").first()
    if not tenant:
        tenant = Tenant(
            name="Default Tenant",
            slug="default"
        )
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        logger.info(f"Tenant created: {tenant.name}")
    else:
        logger.info(f"Tenant already exists: {tenant.name}")

    # 2. Create Global Admin
    user = db.query(User).filter(User.email == settings.FIRST_SUPERUSER).first()
    if not user:
        user = User(
            email=settings.FIRST_SUPERUSER,
            hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
            role=UserRole.GLOBAL_ADMIN,
            is_active=True,
            tenant_id=tenant.id, # Even Global Admin needs a tenant reference for FK usually, or we make it nullable. 
            # In our schema tenant_id is NOT NULL in TenantMixin.
            # So Global Admin MUST belong to a tenant (e.g. "System" or "Default").
            nome="Global Admin"
        )
        db.add(user)
        db.commit()
        logger.info(f"Superuser created: {user.email}")
    else:
        logger.info(f"Superuser already exists: {user.email}")

def main() -> None:
    logger.info("Creating initial data")
    db = SessionLocal()
    init_db(db)
    logger.info("Initial data created")

if __name__ == "__main__":
    main()
