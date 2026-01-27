import uuid
from sqlalchemy import Column, String, Boolean, Time
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base

class Sorteio(Base):
    __tablename__ = "sorteios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String, nullable=False, unique=True)
    horario = Column(Time, nullable=False)
    # limite_apostas removed per user request
    ativo = Column(Boolean, default=True)
