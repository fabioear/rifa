import uuid
import enum
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from app.models.rifa import RifaTipo

class NumeroStatus(str, enum.Enum):
    LIVRE = "livre"
    RESERVADO = "reservado"
    PAGO = "pago"
    EXPIRADO = "expirado"
    CANCELADO = "cancelado"

class PremioStatus(str, enum.Enum):
    PENDING = "PENDING"
    WINNER = "WINNER"
    LOSER = "LOSER"

class RifaNumero(Base):
    __tablename__ = "rifa_numeros"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rifa_id = Column(UUID(as_uuid=True), ForeignKey("rifas.id"), nullable=False)
    
    tipo = Column(Enum(RifaTipo), nullable=False)
    numero = Column(String, nullable=False)
    status = Column(Enum(NumeroStatus), default=NumeroStatus.LIVRE, nullable=False)
    premio_status = Column(Enum(PremioStatus), default=PremioStatus.PENDING, nullable=False)
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)
    
    # New fields for reservation/payment
    payment_id = Column(String, nullable=True)
    reserved_until = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    rifa = relationship("Rifa", back_populates="numeros")
    comprador = relationship("User", foreign_keys=[user_id])
