from sqlalchemy import create_engine, text
from app.core.config import settings

def update_user_name(email, name):
    print(f"Connecting to: {settings.DATABASE_URL}")
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            result = connection.execute(
                text("UPDATE users SET name = :name WHERE email = :email"), 
                {"name": name, "email": email}
            )
            print(f"Rows updated: {result.rowcount}")
            transaction.commit()
            print(f"User {email} updated with name '{name}'")
        except Exception as e:
            transaction.rollback()
            print(f"Error updating user: {e}")

if __name__ == "__main__":
    update_user_name("fabio@teste.com", "Fábio")
