from sqlalchemy import text
from app.db.session import SessionLocal

def inspect_enum():
    db = SessionLocal()
    try:
        # Check actual data
        result = db.execute(text("SELECT status FROM rifas LIMIT 5"))
        print("Data in table:")
        for row in result:
            print(f" - {row[0]}")
            
        # Check enum range again
        result = db.execute(text("SELECT enum_range(NULL::rifastatus)"))
        print(f"Enum definition: {result.fetchone()[0]}")
    except Exception as e:
        print(f"Inspection failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    inspect_enum()
