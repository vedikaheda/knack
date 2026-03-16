import uuid
from sqlalchemy import Column, DateTime, ForeignKey, String, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from ..db.base import Base


class JobExecution(Base):
    __tablename__ = "job_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_type = Column(String, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    trigger_source = Column(String, nullable=False)
    trigger_event_id = Column(String, nullable=True)
    arguments = Column(JSON, nullable=True)
    external_user_id = Column(String, nullable=True)
    provider = Column(String, nullable=True)
    callback_channel = Column(String, nullable=True)
    callback_to = Column(String, nullable=True)
    callback_account_id = Column(String, nullable=True)
    status = Column(String, nullable=False, default="ACCEPTED")
    workflow_execution_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
