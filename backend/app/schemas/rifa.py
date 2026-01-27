from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, field_validator
from app.models.rifa import RifaStatus, RifaTipo, RifaLocal

# Base Schema
class RifaBase(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    preco_numero: float
    tipo_rifa: RifaTipo
    data_sorteio: datetime
    hora_encerramento: Optional[datetime] = None
    local_sorteio: str
    status: RifaStatus = RifaStatus.RASCUNHO

# Create Schema
class RifaCreate(RifaBase):
    pass

# Update Schema
class RifaUpdate(BaseModel):
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    preco_numero: Optional[float] = None
    tipo_rifa: Optional[RifaTipo] = None
    data_sorteio: Optional[datetime] = None
    hora_encerramento: Optional[datetime] = None
    local_sorteio: Optional[str] = None
    status: Optional[RifaStatus] = None

# Status Update Schema
class RifaStatusUpdate(BaseModel):
    status: RifaStatus

# Output Schema
class RifaResponse(RifaBase):
    id: UUID
    owner_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class RifaResultadoBase(BaseModel):
    resultado: str
    local_sorteio: str
    data_resultado: datetime

    @field_validator("resultado")
    @classmethod
    def validate_resultado(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("resultado não pode ser vazio")
        return v


class RifaResultadoCreate(RifaResultadoBase):
    pass


class RifaResultadoResponse(RifaResultadoBase):
    id: UUID
    rifa_id: UUID
    tipo_rifa: RifaTipo
    apurado: bool
    created_at: datetime
    created_by: UUID

    class Config:
        from_attributes = True
