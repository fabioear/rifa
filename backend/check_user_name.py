from sqlalchemy import create_engine, text
from app.core.config import settings

def check_user_name(email):
    print(f"Connecting to: {settings.DATABASE_URL}")
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as connection:
        result = connection.execute(text("SELECT id, email, name, phone FROM users WHERE email = :email"), {"email": email})
        user = result.fetchone()
        
        if user:
            print(f"User found:")
            print(f"ID: {user.id}")
            print(f"Email: {user.email}")
            print(f"Name: {user.name}")
            print(f"Phone: {user.phone}")
        else:
            print(f"User with email {email} not found.")

if __name__ == "__main__":
    check_user_name("fabio@teste.com")
