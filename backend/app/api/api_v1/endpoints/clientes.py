from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.api import deps
from app.services import cliente_service

router = APIRouter()

@router.get("/", response_model=List[schemas.Cliente])
def read_clientes(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve clientes.
    """
    clientes = cliente_service.get_multi(db, skip=skip, limit=limit)
    return clientes

@router.post("/", response_model=schemas.Cliente)
def create_cliente(
    *,
    db: Session = Depends(deps.get_db),
    cliente_in: schemas.ClienteCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new cliente.
    """
    cliente = cliente_service.create(db, obj_in=cliente_in, current_user=current_user)
    return cliente

@router.put("/{id}", response_model=schemas.Cliente)
def update_cliente(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    cliente_in: schemas.ClienteUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a cliente.
    """
    cliente = cliente_service.get(db, id=id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente not found")
    cliente = cliente_service.update(db, db_obj=cliente, obj_in=cliente_in)
    return cliente

@router.get("/{id}", response_model=schemas.Cliente)
def read_cliente(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get cliente by ID.
    """
    cliente = cliente_service.get(db, id=id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente not found")
    return cliente
