from sqlalchemy import create_engine, text
from app.core.config import settings

# Users to KEEP
ADMIN_EMAIL = 'admin@imperiodasrifas.app.br'

print(f"Connecting to: {settings.DATABASE_URL}")

try:
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            # 1. Verify current users
            print("Current users:")
            result = connection.execute(text("SELECT email, role FROM users"))
            for u in result.fetchall():
                print(f"- {u.email} ({u.role})")

            # 2. Delete unwanted admin (admin@example.com)
            # We want to keep the official admin and any players.
            # So we delete specifically admin@example.com OR any admin that is NOT the official one.
            
            delete_query = text("""
                DELETE FROM users 
                WHERE email = 'admin@example.com'
            """)
            
            result = connection.execute(delete_query)
            print(f"\nDeleted users count: {result.rowcount}")

            # 3. Verify remaining users
            print("\nRemaining users:")
            result = connection.execute(text("SELECT email, role FROM users"))
            remaining = result.fetchall()
            for u in remaining:
                print(f"- {u.email} ({u.role})")
            
            transaction.commit()
            print("\nCleanup successful.")
            
        except Exception as e:
            transaction.rollback()
            print(f"Error during cleanup: {e}")
            
except Exception as e:
    print(f"Connection Error: {e}")
