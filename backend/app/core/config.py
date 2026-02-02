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
    
    # Meta / WhatsApp Cloud API
    META_API_URL: str = os.getenv("META_API_URL", "https://graph.facebook.com/v21.0")
    META_ACCESS_TOKEN: str = os.getenv("META_ACCESS_TOKEN", "")
    META_PHONE_NUMBER_ID: str = os.getenv("META_PHONE_NUMBER_ID", "")
    META_WHATSAPP_BUSINESS_ACCOUNT_ID: str = os.getenv("META_WHATSAPP_BUSINESS_ACCOUNT_ID", "")
    META_ENABLED: bool = os.getenv("META_ENABLED", "False").lower() == "true"
    
    # Templates
    TWILIO_TEMPLATE_NEW_RIFA: str = os.getenv("TWILIO_TEMPLATE_NEW_RIFA", "HX41e8ea52f58e61a7f965d94cc27682c7")
    TWILIO_TEMPLATE_WINNER: str = os.getenv("TWILIO_TEMPLATE_WINNER", "HXa99151f37766eed0919a620227b2bdb9")
    
    META_TEMPLATE_NEW_RIFA: str = os.getenv("META_TEMPLATE_NEW_RIFA", "nova_rifa_disponivel")
    META_TEMPLATE_WINNER: str = os.getenv("META_TEMPLATE_WINNER", "rifa_resultado_ganhador")

settings = Settings()
