from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.api import deps
from app.services import rifa_service

router = APIRouter()

@router.get("/", response_model=List[schemas.Rifa])
def read_rifas(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve rifas.
    """
    rifas = rifa_service.get_multi(db, skip=skip, limit=limit)
    return rifas

@router.post("/", response_model=schemas.Rifa)
def create_rifa(
    *,
    db: Session = Depends(deps.get_db),
    rifa_in: schemas.RifaCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new rifa.
    """
    # Verify permissions if needed, e.g. only ADMIN can create rifas
    if current_user.role == models.UserRole.USER:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    rifa = rifa_service.create(db, obj_in=rifa_in, current_user=current_user)
    return rifa

@router.put("/{id}", response_model=schemas.Rifa)
def update_rifa(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    rifa_in: schemas.RifaUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a rifa.
    """
    if current_user.role == models.UserRole.USER:
        raise HTTPException(status_code=400, detail="Not enough permissions")
        
    rifa = rifa_service.get(db, id=id)
    if not rifa:
        raise HTTPException(status_code=404, detail="Rifa not found")
    rifa = rifa_service.update(db, db_obj=rifa, obj_in=rifa_in)
    return rifa

@router.get("/{id}", response_model=schemas.Rifa)
def read_rifa(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get rifa by ID.
    """
    rifa = rifa_service.get(db, id=id)
    if not rifa:
        raise HTTPException(status_code=404, detail="Rifa not found")
    return rifa
