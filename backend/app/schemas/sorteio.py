from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class SorteioBase(BaseModel):
    rifa_id: int
    numero_sorteio: int
    descricao_premio: str
    data_sorteio: Optional[datetime] = None
    ganhador_id: Optional[int] = None

class SorteioCreate(SorteioBase):
    pass

# No Update Schema as per requirement

class Sorteio(SorteioBase):
    id: int
    tenant_id: int

    class Config:
        from_attributes = True
