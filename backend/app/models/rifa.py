import uuid
import enum
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from datetime import timedelta

class RifaStatus(str, enum.Enum):
    RASCUNHO = "rascunho"
    ATIVA = "ativa"
    ENCERRADA = "encerrada"
    APURADA = "apurada"

class RifaTipo(str, enum.Enum):
    MILHAR = "milhar"
    CENTENA = "centena"
    DEZENA = "dezena"
    GRUPO = "grupo"

class RifaTipoResultado(str, enum.Enum):
    MILHAR = "milhar"
    CENTENA = "centena"
    DEZENA = "dezena"
    GRUPO = "grupo"

class RifaLocal(str, enum.Enum):
    PT_RJ = "PT-RJ"
    PTM_RJ = "PTM-RJ"
    CORUJINHA = "Corujinha"
    NACIONAL = "Nacional"
    FEDERAL = "Federal"
    EXTRA = "Extra"
    NOTURNA = "Noturna"
    PERSONALIZADO = "Personalizado"

class Rifa(Base):
    __tablename__ = "rifas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    titulo = Column(String, nullable=False)
    descricao = Column(Text, nullable=True)
    preco_numero = Column(Numeric(10, 2), nullable=False)
    valor_premio = Column(Numeric(10, 2), nullable=True)
    
    tipo_rifa = Column(Enum(RifaTipo), nullable=False)
    
    data_sorteio = Column(DateTime(timezone=True), nullable=False)
    hora_encerramento = Column(DateTime(timezone=True), nullable=True)
    
    local_sorteio = Column(String, nullable=False)
    
    status = Column(Enum(RifaStatus), default=RifaStatus.RASCUNHO, nullable=False)
    
    # New fields for results
    tipo_resultado = Column(Enum(RifaTipoResultado), nullable=True) # Usually same as tipo_rifa but explicit
    resultado = Column(String, nullable=True)

    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    tenant = relationship("Tenant", back_populates="rifas")
    owner = relationship("User", back_populates="rifas")
    numeros = relationship("RifaNumero", back_populates="rifa", cascade="all, delete-orphan")
    resultado_oficial = relationship("RifaResultado", back_populates="rifa", uselist=False)
    ganhadores = relationship("RifaGanhador", back_populates="rifa", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.data_sorteio and not self.hora_encerramento:
            self.hora_encerramento = self.data_sorteio - timedelta(minutes=20)
