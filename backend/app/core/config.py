import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Império das Rifas"
    PROJECT_VERSION: str = "0.1.0"
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

    # Twilio / WhatsApp
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_FROM_NUMBER: str = os.getenv("TWILIO_FROM_NUMBER", "whatsapp:+14155238886")
    TWILIO_ENABLED: bool = os.getenv("TWILIO_ENABLED", "False").lower() == "true"
    
    # Templates
    TWILIO_TEMPLATE_NEW_RIFA: str = os.getenv("TWILIO_TEMPLATE_NEW_RIFA", "HXxxxx_new_rifa")
    TWILIO_TEMPLATE_WINNER: str = os.getenv("TWILIO_TEMPLATE_WINNER", "HXxxxx_winner")

settings = Settings()
