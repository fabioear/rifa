import uuid
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class AdminSettings(Base):
    __tablename__ = "admin_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    
    # Financial Data
    pix_key = Column(String, nullable=True)
    
    # Payment Methods
    accept_pix = Column(Boolean, default=True)
    accept_debito = Column(Boolean, default=False)
    accept_credito = Column(Boolean, default=False)
    
    # Rules
    reservation_timeout_minutes = Column(Integer, default=20)
    fechamento_minutos = Column(Integer, default=20)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="admin_settings")
