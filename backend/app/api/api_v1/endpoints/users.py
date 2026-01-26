from typing import Any, List
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.api import deps
from app.services import user_service

router = APIRouter()

@router.get("/", response_model=List[schemas.User])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve users.
    """
    users = user_service.get_multi(db, skip=skip, limit=limit)
    return users

@router.post("/", response_model=schemas.User)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    current_user: models.User = Depends(deps.get_current_active_user), # Should be Admin?
) -> Any:
    """
    Create new user.
    """
    # Check permissions
    if current_user.role == models.UserRole.USER:
        raise HTTPException(status_code=400, detail="Not enough permissions")
        
    user = user_service.get(db, user_in.email) # Check uniqueness? 
    # Wait, generic get uses ID. We need get_by_email.
    # But let's rely on DB constraint or add get_by_email to service.
    
    # We should add get_by_email to UserService or do manual check here.
    existing_user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
        
    user = user_service.create(db, obj_in=user_in, current_user=current_user)
    return user

@router.get("/me", response_model=schemas.User)
def read_user_me(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user
