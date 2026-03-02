from typing import Any
from sqlalchemy.orm import Session
from ...models.workflow import WorkflowExecution
from ...utils.time import utc_now


class WorkflowRepository:
    def create_execution(
        self, db: Session, transcript_request_id: str, user_id: str, trigger_type: str
    ) -> WorkflowExecution:
        execution = WorkflowExecution(
            transcript_request_id=transcript_request_id,
            user_id=user_id,
            trigger_type=trigger_type,
        )
        db.add(execution)
        db.commit()
        db.refresh(execution)
        return execution

    def get_by_id(self, db: Session, execution_id: str) -> WorkflowExecution | None:
        return db.query(WorkflowExecution).filter(WorkflowExecution.id == execution_id).first()

    def get_latest_for_transcript_request(
        self, db: Session, transcript_request_id: str
    ) -> WorkflowExecution | None:
        return (
            db.query(WorkflowExecution)
            .filter(WorkflowExecution.transcript_request_id == transcript_request_id)
            .order_by(WorkflowExecution.started_at.desc())
            .first()
        )

    def set_status(self, db: Session, execution: WorkflowExecution, status: str) -> WorkflowExecution:
        execution.status = status
        execution.updated_at = utc_now()
        db.commit()
        db.refresh(execution)
        return execution

    def set_current_step(
        self, db: Session, execution: WorkflowExecution, current_step: str | None
    ) -> WorkflowExecution:
        execution.current_step = current_step
        execution.updated_at = utc_now()
        db.commit()
        db.refresh(execution)
        return execution

    def increment_retry(self, db: Session, execution: WorkflowExecution) -> WorkflowExecution:
        execution.retry_count += 1
        execution.updated_at = utc_now()
        db.commit()
        db.refresh(execution)
        return execution

    def set_last_error(self, db: Session, execution: WorkflowExecution, message: str) -> WorkflowExecution:
        execution.last_error = message
        execution.updated_at = utc_now()
        db.commit()
        db.refresh(execution)
        return execution

    def update_context(
        self, db: Session, execution: WorkflowExecution, context: dict[str, Any]
    ) -> WorkflowExecution:
        execution.context = context
        execution.updated_at = utc_now()
        db.commit()
        db.refresh(execution)
        return execution

    def mark_failed(
        self, db: Session, execution: WorkflowExecution, message: str, current_step: str | None
    ) -> WorkflowExecution:
        execution.status = "FAILED"
        execution.current_step = current_step
        execution.last_error = message
        execution.updated_at = utc_now()
        db.commit()
        db.refresh(execution)
        return execution

    def mark_completed(self, db: Session, execution: WorkflowExecution) -> WorkflowExecution:
        execution.status = "COMPLETED"
        execution.current_step = None
        execution.completed_at = utc_now()
        execution.updated_at = utc_now()
        db.commit()
        db.refresh(execution)
        return execution
