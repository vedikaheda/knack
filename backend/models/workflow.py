import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from ..db.base import Base


class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_type = Column(String, nullable=False, default="GenerateBRDFromTranscriptLink")
    transcript_request_id = Column(
        UUID(as_uuid=True), ForeignKey("transcript_requests.id"), nullable=False
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    trigger_type = Column(String, nullable=False, default="UI")
    status = Column(String, nullable=False, default="PENDING")
    current_step = Column(String, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    last_error = Column(String, nullable=True)
    context = Column(JSON, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
