import uuid
from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from ..db.base import Base


class UserExternalIdentity(Base):
    __tablename__ = "user_external_identities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    provider = Column(String, nullable=False)
    external_user_id = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
