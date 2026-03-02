from sqlalchemy.orm import Session
from .repository import JobRepository


class JobService:
    def __init__(self) -> None:
        self.repo = JobRepository()

    def get_by_id(self, db: Session, job_id: str):
        return self.repo.get_by_id(db, job_id)

    def get_by_trigger_event_id(self, db: Session, trigger_event_id: str):
        return self.repo.get_by_trigger_event_id(db, trigger_event_id)

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
    ):
        return self.repo.create(
            db,
            job_type,
            user_id,
            trigger_source,
            trigger_event_id,
            arguments,
            external_user_id=external_user_id,
            provider=provider,
        )

    def set_status(self, db: Session, job_id: str, status: str):
        job = self.repo.get_by_id(db, job_id)
        if not job:
            return None
        return self.repo.set_status(db, job, status)

    def set_workflow_execution_id(self, db: Session, job_id: str, workflow_execution_id: str):
        job = self.repo.get_by_id(db, job_id)
        if not job:
            return None
        return self.repo.set_workflow_execution_id(db, job, workflow_execution_id)

    def mark_completed(self, db: Session, job_id: str):
        job = self.repo.get_by_id(db, job_id)
        if not job:
            return None
        return self.repo.mark_completed(db, job)

    def mark_failed(self, db: Session, job_id: str):
        job = self.repo.get_by_id(db, job_id)
        if not job:
            return None
        return self.repo.mark_failed(db, job)
