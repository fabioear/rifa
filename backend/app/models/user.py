import enum
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer
from sqlalchemy.sql import func
from app.db.base_class import Base
from app.db.mixins import TenantMixin
from sqlalchemy.orm import relationship

class UserRole(str, enum.Enum):
    GLOBAL_ADMIN = "GLOBAL_ADMIN"
    ADMIN = "ADMIN" # Tenant Admin
    USER = "USER"   # Tenant User

class UserTheme(str, enum.Enum):
    LIGHT = "light"
    DARK = "dark"

class User(Base, TenantMixin):
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    theme = Column(Enum(UserTheme), default=UserTheme.LIGHT, nullable=False)
    is_active = Column(Boolean(), default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tenant = relationship("Tenant", back_populates="users")
