import logging
from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from ..deps import get_db
from ...core.database import SessionLocal
from ...modules.auth.service import AuthService
from ...modules.job.schemas import JobExecuteRequest
from ...modules.job.service import JobService
from ...modules.transcript_request.service import TranscriptRequestService
from ...modules.user.service import UserService
from ...modules.workflow.service import WorkflowService
from ...modules.integration.openclaw import OpenClawHookError, send_hook


router = APIRouter()
logger = logging.getLogger(__name__)


def _build_openclaw_payload(execution, event_type: str) -> dict:
    context = execution.context or {}
    channel = context.get("channel")
    callback_to = context.get("to")
    account_id = context.get("account_id")
    if not channel or not callback_to:
        raise OpenClawHookError("Missing channel or to for OpenClaw delivery")

    google_doc_id = context.get("google_doc_id")
    google_doc_url = (
        f"https://docs.google.com/document/d/{google_doc_id}/edit" if google_doc_id else None
    )

    if event_type == "workflow.completed":
        message = (
            f"Your BRD is ready: {google_doc_url}" if google_doc_url else "Your BRD is ready."
        )
    else:
        message = "Workflow failed. Please try again."
        if execution.last_error:
            message = f"Workflow failed: {execution.last_error}"

    payload = {
        "message": message,
        "name": event_type,
        "deliver": True,
        "channel": channel,
        "to": callback_to,
        "wakeMode": "now",
    }
    if account_id:
        payload["accountId"] = account_id
    return payload


def _extract_slack_user_id(callback_to: str) -> str:
    if not callback_to.startswith("user:"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Slack DM callback targets are supported",
        )
    slack_user_id = callback_to.removeprefix("user:")
    if not slack_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid callback target",
        )
    return slack_user_id


def _run_workflow_job(job_id: str, execution_id: str) -> None:
    db = SessionLocal()
    try:
        workflow_service = WorkflowService()
        job_service = JobService()

        execution = workflow_service.run(db, execution_id)
        if execution.status == "COMPLETED":
            job_service.mark_completed(db, job_id)
        else:
            job_service.mark_failed(db, job_id)

        event_type = (
            "workflow.completed" if execution.status == "COMPLETED" else "workflow.failed"
        )
        try:
            payload = _build_openclaw_payload(execution, event_type)
            send_hook(payload)
        except OpenClawHookError as exc:
            logger.error("OpenClaw hook failed: %s", exc)
            context = execution.context or {}
            context["webhook_error"] = str(exc)
            workflow_service.update_context(db, str(execution.id), context)
    except Exception as exc:
        logger.exception("Background workflow failed: %s", exc)
        job_service = JobService()
        job_service.mark_failed(db, job_id)
    finally:
        db.close()


@router.post("/execute")
def execute_job(
    payload: JobExecuteRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None),
):
    auth_service = AuthService()
    token = authorization.replace("Bearer ", "") if authorization else ""
    if not auth_service.verify_service_token(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    if payload.job not in {"create_brd_from_transcript", "regenerate_brd"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported job")

    channel = payload.context.get("channel")
    callback_to = payload.context.get("to")
    account_id = payload.context.get("account_id")
    if not channel or not callback_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing channel or to",
        )
    if channel != "slack":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported callback channel",
        )
    slack_user_id = _extract_slack_user_id(callback_to)

    user_service = UserService()
    user = user_service.get_by_external_identity(db, "slack", slack_user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    job_service = JobService()
    request_service = TranscriptRequestService()
    if payload.job == "create_brd_from_transcript":
        transcript_link = payload.arguments.get("transcript_link")
        if not transcript_link:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Missing transcript_link"
            )
        request = request_service.create(db, str(user.id), transcript_link)
    else:
        request_id = payload.arguments.get("transcript_request_id")
        if not request_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing transcript_request_id",
            )
        request = request_service.get(db, request_id)
        if not request or str(request.user_id) != str(user.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transcript request not found",
            )

    job = job_service.create(
        db,
        job_type=payload.job,
        user_id=str(user.id),
        trigger_source="slack",
        trigger_event_id=None,
        arguments=payload.arguments,
        external_user_id=slack_user_id,
        provider="slack",
        callback_channel=channel,
        callback_to=callback_to,
        callback_account_id=account_id,
    )

    workflow_service = WorkflowService()
    execution = workflow_service.create_execution(
        db, str(request.id), str(user.id), "SLACK"
    )
    workflow_service.update_context(db, str(execution.id), payload.context)
    job_service.set_workflow_execution_id(db, str(job.id), str(execution.id))
    job_service.set_status(db, str(job.id), "RUNNING")

    background_tasks.add_task(_run_workflow_job, str(job.id), str(execution.id))

    return {
        "status": "accepted",
        "job_execution_id": str(job.id),
        "workflow_execution_id": str(execution.id),
    }
