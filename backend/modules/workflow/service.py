from sqlalchemy.orm import Session
from .engine import WorkflowEngine
from .repository import WorkflowRepository


class WorkflowService:
    def __init__(self) -> None:
        self.repo = WorkflowRepository()
        self.engine = WorkflowEngine()

    def create_execution(
        self, db: Session, transcript_request_id: str, user_id: str, trigger_type: str
    ):
        return self.repo.create_execution(db, transcript_request_id, user_id, trigger_type)

    def get_execution(self, db: Session, execution_id: str):
        return self.repo.get_by_id(db, execution_id)

    def get_execution_for_transcript_request(self, db: Session, transcript_request_id: str):
        return self.repo.get_latest_for_transcript_request(db, transcript_request_id)

    def run(self, db: Session, execution_id: str, max_step_retries: int = 3):
        return self.engine.run(db, execution_id, max_step_retries=max_step_retries)

    def update_context(self, db: Session, execution_id: str, context: dict):
        execution = self.repo.get_by_id(db, execution_id)
        if not execution:
            return None
        return self.repo.update_context(db, execution, context)
