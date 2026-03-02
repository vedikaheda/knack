import logging
from sqlalchemy.orm import Session
from .repository import WorkflowRepository
from .steps import WORKFLOW_STEPS, StepDefinition

logger = logging.getLogger(__name__)


class WorkflowEngine:
    def __init__(self) -> None:
        self.repo = WorkflowRepository()

    def run(self, db: Session, execution_id: str, max_step_retries: int = 3):
        execution = self.repo.get_by_id(db, execution_id)
        if not execution:
            raise ValueError(f"WorkflowExecution not found: {execution_id}")

        if execution.status == "COMPLETED":
            return execution

        context = execution.context or {}
        completed_steps = set(context.get("completed_steps", []))

        for step in WORKFLOW_STEPS:
            if step.key in completed_steps:
                continue

            execution = self.repo.set_status(db, execution, "RUNNING")
            execution = self.repo.set_current_step(db, execution, step.key)
            result = self._run_step_with_retries(
                db=db,
                execution=execution,
                step=step,
                context=context,
                max_step_retries=max_step_retries,
            )
            if result is False:
                return execution

            context.setdefault("completed_steps", []).append(step.key)
            if result:
                context.setdefault("step_outputs", {})[step.key] = result
            execution = self.repo.update_context(db, execution, context)

        execution = self.repo.mark_completed(db, execution)
        return execution

    def _run_step_with_retries(
        self,
        db: Session,
        execution,
        step: StepDefinition,
        context: dict,
        max_step_retries: int,
    ):
        if not step.retryable:
            try:
                return step.handler(db, execution, context)
            except Exception as exc:
                message = f"{step.key} failed: {exc}"
                logger.exception(message)
                self.repo.mark_failed(db, execution, message, step.key)
                return False

        attempts = 0
        while attempts < max_step_retries:
            try:
                return step.handler(db, execution, context)
            except Exception as exc:
                attempts += 1
                message = f"{step.key} failed (attempt {attempts}/{max_step_retries}): {exc}"
                logger.exception(message)
                self.repo.increment_retry(db, execution)
                self.repo.set_last_error(db, execution, message)

        final_message = f"{step.key} failed after {max_step_retries} attempts"
        logger.error(final_message)
        self.repo.mark_failed(db, execution, final_message, step.key)
        return False
