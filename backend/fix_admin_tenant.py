from sqlalchemy import create_engine, text
from app.core.config import settings

# Production Tenant ID from previous check: 650d3529-0450-4304-8ca6-1e4eda43c045
PROD_TENANT_ID = '650d3529-0450-4304-8ca6-1e4eda43c045'
ADMIN_EMAIL = 'admin@imperiodasrifas.app.br'

print(f"Connecting to: {settings.DATABASE_URL}")

try:
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            # Update the admin user to belong to the production tenant
            result = connection.execute(
                text("UPDATE users SET tenant_id = :tenant_id WHERE email = :email"),
                {"tenant_id": PROD_TENANT_ID, "email": ADMIN_EMAIL}
            )
            print(f"Updated admin user tenant. Rows affected: {result.rowcount}")
            
            # Also update the other admin just in case
            connection.execute(
                text("UPDATE users SET tenant_id = :tenant_id WHERE email = :email"),
                {"tenant_id": PROD_TENANT_ID, "email": "admin@example.com"}
            )
            
            transaction.commit()
            print("Successfully moved admin users to Production Tenant.")
        except Exception as e:
            transaction.rollback()
            print(f"Error during update: {e}")
            
except Exception as e:
    print(f"Connection Error: {e}")
