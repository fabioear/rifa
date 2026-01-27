import uuid
from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class RifaGanhador(Base):
    __tablename__ = "rifa_ganhadores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rifa_id = Column(UUID(as_uuid=True), ForeignKey("rifas.id"), nullable=False)
    rifa_numero_id = Column(UUID(as_uuid=True), ForeignKey("rifa_numeros.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    rifa = relationship("Rifa", back_populates="ganhadores")
    numero = relationship("RifaNumero")
    user = relationship("User")

