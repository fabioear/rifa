from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Tenant(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    
    users = relationship("User", back_populates="tenant")
    clientes = relationship("Cliente", back_populates="tenant")
    rifas = relationship("Rifa", back_populates="tenant")
