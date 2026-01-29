from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api import deps
from app.core.config import settings
from app.core import security
from app.models.user import User
from pydantic import BaseModel
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.api.deps import get_current_active_user

router = APIRouter()

@router.get("/users/me", response_model=UserResponse)
def read_users_me(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get current user.
    """
    return current_user

@router.patch("/users/me", response_model=UserResponse)
def update_user_me(
    user_in: UserUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update current user.
    """
    if user_in.email is not None and user_in.email != current_user.email:
         # Check if email already exists
         user = db.query(User).filter(User.email == user_in.email).first()
         if user:
             raise HTTPException(
                 status_code=400,
                 detail="Email already registered",
             )
         current_user.email = user_in.email

    if user_in.password is not None:
        current_user.password_hash = security.get_password_hash(user_in.password)
    if user_in.name is not None:
        current_user.name = user_in.name
    if user_in.phone is not None:
        current_user.phone = user_in.phone
    if user_in.whatsapp_opt_in is not None:
        current_user.whatsapp_opt_in = user_in.whatsapp_opt_in
    
    db.commit()
    db.refresh(current_user)
    return current_user


class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/login/access-token", response_model=Token)
def login_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(deps.get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": str(user.id), "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

from app.models.tenant import Tenant
from app.core.tenant import get_tenant_by_host

@router.post("/users", response_model=UserResponse)
def create_user(
    user_in: UserCreate, 
    db: Session = Depends(deps.get_db),
    current_tenant: Tenant = Depends(get_tenant_by_host)
):
    """
    Create new user (Open for now, for testing).
    """
    # Check if user exists in THIS tenant
    user = db.query(User).filter(
        User.email == user_in.email,
        User.tenant_id == current_tenant.id
    ).first()
    
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = User(
        email=user_in.email,
        password_hash=security.get_password_hash(user_in.password),
        is_active=True,
        role="player", # Default role
        tenant_id=current_tenant.id,
        phone=user_in.phone,
        whatsapp_opt_in=user_in.whatsapp_opt_in,
        name=user_in.name
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
