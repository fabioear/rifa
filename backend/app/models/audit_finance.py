import uuid
import enum
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, Enum, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class PaymentLogMethod(str, enum.Enum):
    PIX = "pix"
    DEBITO = "debito"
    CREDITO = "credito"

class PaymentLogStatus(str, enum.Enum):
    PAGO = "pago"
    CANCELADO = "cancelado"
    ESTORNADO = "estornado"

class PaymentLog(Base):
    __tablename__ = "payment_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rifa_id = Column(UUID(as_uuid=True), ForeignKey("rifas.id"), nullable=False)
    numero_id = Column(UUID(as_uuid=True), ForeignKey("rifa_numeros.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)
    
    payment_id = Column(String, nullable=False)
    valor = Column(Numeric(10, 2), nullable=False)
    metodo = Column(Enum(PaymentLogMethod), nullable=False)
    status = Column(Enum(PaymentLogStatus), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_id = Column(UUID(as_uuid=True), nullable=True) # Nullable for system actions? Or use specific system ID
    actor_role = Column(String, nullable=True)
    action = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
