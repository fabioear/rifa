from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.models.user import UserRole, UserTheme

class UserBase(BaseModel):
    email: EmailStr
    nome: Optional[str] = None
    role: UserRole = UserRole.USER
    theme: UserTheme = UserTheme.LIGHT
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str
    tenant_id: int

class UserUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    theme: Optional[UserTheme] = None
    is_active: Optional[bool] = None

class User(UserBase):
    id: int
    tenant_id: int
    created_at: datetime

    class Config:
        from_attributes = True
