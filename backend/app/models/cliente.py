from sqlalchemy import Column, String, Integer
from app.db.base_class import Base
from app.db.mixins import TenantMixin
from sqlalchemy.orm import relationship

class Cliente(Base, TenantMixin):
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    email = Column(String, index=True)
    telefone = Column(String)
    
    tenant = relationship("Tenant", back_populates="clientes")
    rifas_compradas = relationship("Sorteio", back_populates="ganhador") # Exemplo, ou compras...
    # For simplicity, just basic info now.
