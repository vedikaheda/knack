import uuid
from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from ..db.base import Base


class TranscriptRequest(Base):
    __tablename__ = "transcript_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    source_link = Column(String, nullable=False)
    status = Column(String, nullable=False, default="SUBMITTED")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
