from sqlalchemy import create_engine, text
from app.core.config import settings

def add_name_column():
    print(f"Connecting to: {settings.DATABASE_URL}")
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            # Check if column exists
            result = connection.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='name'"))
            if result.fetchone():
                print("Column 'name' already exists.")
            else:
                print("Adding column 'name' to table 'users'...")
                connection.execute(text("ALTER TABLE users ADD COLUMN name VARCHAR"))
                print("Column added successfully.")
            
            transaction.commit()
        except Exception as e:
            transaction.rollback()
            print(f"Error: {e}")

if __name__ == "__main__":
    add_name_column()
