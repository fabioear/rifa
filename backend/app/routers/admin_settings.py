from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_active_superuser
from app.models.admin_settings import AdminSettings
from app.models.user import User
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class AdminSettingsUpdate(BaseModel):
    fechamento_minutos: Optional[int] = None

class AdminSettingsResponse(BaseModel):
    fechamento_minutos: int

@router.get("/settings", response_model=AdminSettingsResponse)
def get_admin_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    settings = db.query(AdminSettings).filter(AdminSettings.user_id == current_user.id).first()
    if not settings:
        # Create default settings if not exists
        settings = AdminSettings(user_id=current_user.id, fechamento_minutos=20)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return {"fechamento_minutos": settings.fechamento_minutos}

@router.put("/settings", response_model=AdminSettingsResponse)
def update_admin_settings(
    settings_in: AdminSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    settings = db.query(AdminSettings).filter(AdminSettings.user_id == current_user.id).first()
    if not settings:
        settings = AdminSettings(user_id=current_user.id)
        db.add(settings)
    
    if settings_in.fechamento_minutos is not None:
        settings.fechamento_minutos = settings_in.fechamento_minutos
        
    db.commit()
    db.refresh(settings)
    return {"fechamento_minutos": settings.fechamento_minutos}
