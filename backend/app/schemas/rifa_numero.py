from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.rifa import RifaTipo
from app.models.rifa_numero import NumeroStatus, PremioStatus

class RifaNumeroBase(BaseModel):
    numero: str
    tipo: RifaTipo

class RifaNumeroCreate(RifaNumeroBase):
    rifa_id: UUID

class RifaNumeroUpdate(BaseModel):
    status: Optional[NumeroStatus] = None
    premio_status: Optional[PremioStatus] = None
    user_id: Optional[UUID] = None
    payment_id: Optional[str] = None
    reserved_until: Optional[datetime] = None

class RifaNumeroResponse(RifaNumeroBase):
    id: UUID
    rifa_id: UUID
    status: NumeroStatus
    premio_status: PremioStatus = PremioStatus.PENDING
    user_id: Optional[UUID] = None
    created_at: datetime
    reserved_until: Optional[datetime] = None
    payment_id: Optional[str] = None
    is_owner: bool = False  # Computed field

    class Config:
        from_attributes = True
