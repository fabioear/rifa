import uuid
from sqlalchemy import Column, String, Boolean, TIMESTAMP, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True) # Nullable for super-admin or migration? Better strict.
    name = Column(String, nullable=True)
    email = Column(String, nullable=False, index=True) # Unique per tenant logic handled by app or composite constraint? 
    # Prompt says "tudo passa a ser: tenant_id". For simplicity, let's keep email unique globally for now OR composite.
    # If I remove unique=True, I must handle it in code.
    # Let's try to make it unique per tenant if possible, but SQLAlchemy composite unique requires __table_args__.
    
    password_hash = Column(String, nullable=False)
    role = Column(String, default="player")
    is_active = Column(Boolean, default=True)
    phone = Column(String, nullable=True)
    whatsapp_opt_in = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    
    tenant = relationship("Tenant", back_populates="users")
    rifas = relationship("Rifa", back_populates="owner")
    admin_settings = relationship("AdminSettings", back_populates="user", uselist=False)
