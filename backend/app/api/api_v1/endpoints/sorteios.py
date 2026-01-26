from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.api import deps
from app.services import sorteio_service, rifa_service

router = APIRouter()

@router.get("/", response_model=List[schemas.Sorteio])
def read_sorteios(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve sorteios.
    """
    sorteios = sorteio_service.get_multi(db, skip=skip, limit=limit)
    return sorteios

@router.post("/", response_model=schemas.Sorteio)
def create_sorteio(
    *,
    db: Session = Depends(deps.get_db),
    sorteio_in: schemas.SorteioCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new sorteio.
    """
    if current_user.role == models.UserRole.USER:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    # Verify if Rifa exists
    rifa = rifa_service.get(db, id=sorteio_in.rifa_id)
    if not rifa:
        raise HTTPException(status_code=404, detail="Rifa not found")

    sorteio = sorteio_service.create(db, obj_in=sorteio_in, current_user=current_user)
    return sorteio

@router.get("/{id}", response_model=schemas.Sorteio)
def read_sorteio(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get sorteio by ID.
    """
    sorteio = sorteio_service.get(db, id=id)
    if not sorteio:
        raise HTTPException(status_code=404, detail="Sorteio not found")
    return sorteio

# Update is NOT allowed as per requirements: "Sorteios não podem ser editados após criados"
# But maybe we need to set the winner?
# Requirement says "Sorteios não podem ser editados após criados".
# Usually setting a winner is an update.
# I will implement a specific endpoint to set winner if needed, or assume "edit" means structural changes.
# Given "Sorteios não podem ser editados", I will stick to strictly NO update for now to satisfy requirement.
# If setting winner is required, it should probably be a separate action "draw" or similar.
