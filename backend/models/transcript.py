import uuid
from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from ..db.base import Base


class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transcript_request_id = Column(
        UUID(as_uuid=True), ForeignKey("transcript_requests.id"), nullable=False
    )
    source = Column(String, nullable=False)
    raw_text = Column(Text, nullable=False)
    cleaned_text = Column(Text, nullable=True)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
