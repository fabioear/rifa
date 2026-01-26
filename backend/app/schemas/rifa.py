from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
# from .sorteio import Sorteio # Circular dependency, use ForwardRef or skip if not nested response needed

class RifaBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    preco_bilhete: float
    ativo: Optional[bool] = True

class RifaCreate(RifaBase):
    pass

class RifaUpdate(RifaBase):
    pass

class Rifa(RifaBase):
    id: int
    tenant_id: int
    data_inicio: datetime

    class Config:
        from_attributes = True
