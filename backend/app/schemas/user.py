from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
import uuid

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    is_active: Optional[bool] = True
    role: Optional[str] = "player"
    phone: Optional[str] = None
    whatsapp_opt_in: Optional[bool] = False

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None
    phone: Optional[str] = None
    whatsapp_opt_in: Optional[bool] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: uuid.UUID
    created_at: datetime
    
    class Config:
        from_attributes = True
