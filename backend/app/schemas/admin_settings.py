from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class AdminSettingsBase(BaseModel):
    pix_key: Optional[str] = None
    accept_pix: bool = True
    accept_debito: bool = False
    accept_credito: bool = False
    reservation_timeout_minutes: int = 20
    fechamento_minutos: int = 20

class AdminSettingsCreate(AdminSettingsBase):
    pass

class AdminSettingsUpdate(AdminSettingsBase):
    pass

class AdminSettingsResponse(AdminSettingsBase):
    id: UUID
    user_id: UUID

    class Config:
        from_attributes = True
