import uuid
from sqlalchemy import Column, String, TIMESTAMP, text, Enum
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import enum

class BlockedEntityType(str, enum.Enum):
    IP = "ip"
    USER = "user"

class BlockedEntity(Base):
    __tablename__ = "blocked_entities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(Enum(BlockedEntityType), nullable=False)
    value = Column(String, nullable=False, index=True) # IP address or User ID string
    reason = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    tenant_id = Column(UUID(as_uuid=True), nullable=True) # Optional for global blocks, but usually tenant specific
