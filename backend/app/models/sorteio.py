from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.db.mixins import TenantMixin

class Sorteio(Base, TenantMixin):
    id = Column(Integer, primary_key=True, index=True)
    rifa_id = Column(Integer, ForeignKey("rifa.id"), nullable=False)
    numero_sorteio = Column(Integer, nullable=False) # e.g. 1st prize, 2nd prize
    descricao_premio = Column(String, nullable=False)
    data_sorteio = Column(DateTime(timezone=True))
    
    ganhador_id = Column(Integer, ForeignKey("cliente.id"), nullable=True)
    
    rifa = relationship("Rifa", back_populates="sorteios")
    ganhador = relationship("Cliente")
