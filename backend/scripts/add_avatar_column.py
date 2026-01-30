import sys
import os
from sqlalchemy import text

# Add the backend directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.session import engine

def add_avatar_column():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN avatar_url VARCHAR"))
            conn.commit()
            print("Successfully added avatar_url column to users table.")
        except Exception as e:
            print(f"Error (column might already exist): {e}")

if __name__ == "__main__":
    add_avatar_column()
