from typing import Optional
from datetime import time
from uuid import UUID
from pydantic import BaseModel

class SorteioBase(BaseModel):
    nome: str
    horario: time
    ativo: bool = True

class SorteioCreate(SorteioBase):
    pass

class SorteioUpdate(BaseModel):
    nome: Optional[str] = None
    horario: Optional[time] = None
    ativo: Optional[bool] = None

class SorteioResponse(SorteioBase):
    id: UUID

    class Config:
        from_attributes = True
