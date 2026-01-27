from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.config import settings
from app.models.user import User
from app.models.tenant import Tenant
from app.core.tenant import get_tenant_by_host
from pydantic import BaseModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login/access-token")

class TokenData(BaseModel):
    id: Optional[str] = None
    role: Optional[str] = None

def get_current_user(
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2_scheme),
    current_tenant: Tenant = Depends(get_tenant_by_host)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(id=user_id, role=role)
    except JWTError:
        raise credentials_exception
    
    # Ensure user belongs to the current tenant
    user = db.query(User).filter(User.id == token_data.id, User.tenant_id == current_tenant.id).first()
    if user is None:
        # Check if user exists but in another tenant (security measure)
        # For now, just raise credentials exception
        raise credentials_exception
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_active_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user
