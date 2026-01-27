from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.models.sorteio import Sorteio
from app.schemas.sorteio import SorteioResponse, SorteioCreate, SorteioUpdate
from app.api.deps import get_current_active_superuser as get_current_admin_user

router = APIRouter(
    prefix="/sorteios",
    tags=["sorteios"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[SorteioResponse])
def list_sorteios(
    skip: int = 0, 
    limit: int = 100, 
    only_active: bool = True,
    db: Session = Depends(get_db)
):
    query = db.query(Sorteio)
    if only_active:
        query = query.filter(Sorteio.ativo == True)
    return query.offset(skip).limit(limit).all()

@router.post("/", response_model=SorteioResponse)
def create_sorteio(
    sorteio: SorteioCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    db_sorteio = Sorteio(**sorteio.dict())
    db.add(db_sorteio)
    try:
        db.commit()
        db.refresh(db_sorteio)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return db_sorteio

@router.put("/{sorteio_id}", response_model=SorteioResponse)
def update_sorteio(
    sorteio_id: UUID, 
    sorteio_update: SorteioUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    db_sorteio = db.query(Sorteio).filter(Sorteio.id == sorteio_id).first()
    if not db_sorteio:
        raise HTTPException(status_code=404, detail="Sorteio not found")
    
    for key, value in sorteio_update.dict(exclude_unset=True).items():
        setattr(db_sorteio, key, value)
    
    db.commit()
    db.refresh(db_sorteio)
    return db_sorteio

@router.delete("/{sorteio_id}")
def delete_sorteio(
    sorteio_id: UUID, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    db_sorteio = db.query(Sorteio).filter(Sorteio.id == sorteio_id).first()
    if not db_sorteio:
        raise HTTPException(status_code=404, detail="Sorteio not found")
    
    db.delete(db_sorteio)
    db.commit()
    return {"ok": True}
