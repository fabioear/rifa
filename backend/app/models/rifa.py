from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.db.mixins import TenantMixin

class Rifa(Base, TenantMixin):
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True, nullable=False)
    descricao = Column(String)
    preco_bilhete = Column(Float, nullable=False)
    data_inicio = Column(DateTime(timezone=True), default=func.now())
    ativo = Column(Boolean, default=True)

    tenant = relationship("Tenant", back_populates="rifas")
    sorteios = relationship("Sorteio", back_populates="rifa", cascade="all, delete-orphan")
