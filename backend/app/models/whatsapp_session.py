from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.sql import func
from app.db.base import Base

class WhatsappSession(Base):
    __tablename__ = "whatsapp_sessions"

    phone_number = Column(String, primary_key=True, index=True)
    step = Column(String, default="MENU")
    temp_data = Column(JSON, default={})
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
