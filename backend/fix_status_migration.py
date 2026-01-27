from sqlalchemy import text
from app.db.session import SessionLocal

def migrate_status():
    db = SessionLocal()
    try:
        print("Starting migration: DRAFT -> RASCUNHO...")
        # Rename uppercase DRAFT to RASCUNHO
        db.execute(text("ALTER TYPE rifastatus RENAME VALUE 'DRAFT' TO 'RASCUNHO'"))
        db.commit()
        print("Migration successful: DRAFT -> RASCUNHO")
    except Exception as e:
        print(f"Migration failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_status()
