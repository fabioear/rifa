import uuid
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from app.models.rifa import RifaTipo


class RifaResultado(Base):
    __tablename__ = "rifa_resultados"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rifa_id = Column(UUID(as_uuid=True), ForeignKey("rifas.id"), nullable=False, unique=True)
    tipo_rifa = Column(Enum(RifaTipo), nullable=False)
    resultado = Column(String, nullable=False)
    local_sorteio = Column(String, nullable=False)
    data_resultado = Column(DateTime(timezone=True), nullable=False)
    apurado = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)

    rifa = relationship("Rifa", back_populates="resultado_oficial")
    creator = relationship("User")

