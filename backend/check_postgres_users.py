from sqlalchemy import create_engine, text
from app.core.config import settings

# Override settings to ensure we use the .env values if needed, 
# but settings should load from .env automatically.
# We will just use settings.DATABASE_URL

print(f"Connecting to: {settings.DATABASE_URL}")

try:
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as connection:
        # Check Tenants
        result = connection.execute(text("SELECT id, name, domain FROM tenants"))
        tenants = result.fetchall()
        print(f"\nTenants in DB: {len(tenants)}")
        for t in tenants:
            print(f"- {t}")

        # Check Users
        result = connection.execute(text("SELECT email, role, is_active, tenant_id FROM users"))
        users = result.fetchall()
        print(f"\nTotal users in DB: {len(users)}")
        for user in users:
            print(f"- {user}")
except Exception as e:
    print(f"Error: {e}")
