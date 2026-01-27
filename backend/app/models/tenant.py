import uuid
from sqlalchemy import Column, String, TIMESTAMP, JSON, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    domain = Column(String, unique=True, nullable=False, index=True)
    logo_url = Column(String, nullable=True)
    primary_color = Column(String, nullable=True)
    secondary_color = Column(String, nullable=True)
    pix_key = Column(String, nullable=True)
    picpay_config = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))

    # Relationships
    users = relationship("User", back_populates="tenant")
    rifas = relationship("Rifa", back_populates="tenant")
