from sqlalchemy.orm import Session
from ...models.job_execution import JobExecution
from ...utils.time import utc_now


class JobRepository:
    def get_by_id(self, db: Session, job_id: str) -> JobExecution | None:
        return db.query(JobExecution).filter(JobExecution.id == job_id).first()

    def get_by_trigger_event_id(self, db: Session, trigger_event_id: str) -> JobExecution | None:
        return (
            db.query(JobExecution)
            .filter(JobExecution.trigger_event_id == trigger_event_id)
            .first()
        )

    def create(
        self,
        db: Session,
        job_type: str,
        user_id: str,
        trigger_source: str,
        trigger_event_id: str | None,
        arguments: dict | None,
        external_user_id: str | None = None,
        provider: str | None = None,
    ) -> JobExecution:
        job = JobExecution(
            job_type=job_type,
            user_id=user_id,
            trigger_source=trigger_source,
            trigger_event_id=trigger_event_id,
            arguments=arguments,
            external_user_id=external_user_id,
            provider=provider,
            status="ACCEPTED",
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    def set_status(self, db: Session, job: JobExecution, status: str) -> JobExecution:
        job.status = status
        db.commit()
        db.refresh(job)
        return job

    def set_workflow_execution_id(
        self, db: Session, job: JobExecution, workflow_execution_id: str
    ) -> JobExecution:
        job.workflow_execution_id = workflow_execution_id
        db.commit()
        db.refresh(job)
        return job

    def mark_completed(self, db: Session, job: JobExecution) -> JobExecution:
        job.status = "COMPLETED"
        job.completed_at = utc_now()
        db.commit()
        db.refresh(job)
        return job

    def mark_failed(self, db: Session, job: JobExecution) -> JobExecution:
        job.status = "FAILED"
        job.completed_at = utc_now()
        db.commit()
        db.refresh(job)
        return job
