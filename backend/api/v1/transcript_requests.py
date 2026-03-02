from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..deps import get_current_user
from ...core.database import get_db
from ...modules.transcript_request.schemas import TranscriptRequestCreate
from ...modules.transcript_request.service import TranscriptRequestService
from ...modules.user.service import UserService
from ...modules.job.service import JobService
from ...modules.workflow.service import WorkflowService


router = APIRouter()


@router.get("/")
def list_transcript_requests(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user_service = UserService()
    user = user_service.get_by_email(db, current_user.get("email"))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    service = TranscriptRequestService()
    items = service.list_by_user(db, str(user.id))
    return {"items": items}


@router.get("/{request_id}")
def get_transcript_request(
    request_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user_service = UserService()
    user = user_service.get_by_email(db, current_user.get("email"))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    service = TranscriptRequestService()
    request = service.get(db, request_id)
    if not request or str(request.user_id) != str(user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transcript request not found")
    return request


@router.post("/")
def create_transcript_request(
    payload: TranscriptRequestCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user_service = UserService()
    user = user_service.get_by_email(db, current_user.get("email"))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    request_service = TranscriptRequestService()
    request = request_service.create(db, str(user.id), payload.source_link)

    job_service = JobService()
    job = job_service.create(
        db,
        job_type="create_brd_from_transcript",
        user_id=str(user.id),
        trigger_source="ui",
        trigger_event_id=None,
        arguments={"transcript_link": payload.source_link},
    )

    workflow_service = WorkflowService()
    execution = workflow_service.create_execution(
        db, str(request.id), str(user.id), "UI"
    )
    job_service.set_workflow_execution_id(db, str(job.id), str(execution.id))
    job_service.set_status(db, str(job.id), "RUNNING")
    execution = workflow_service.run(db, str(execution.id))
    if execution.status == "COMPLETED":
        job_service.mark_completed(db, str(job.id))
    else:
        job_service.mark_failed(db, str(job.id))

    return {
        "request_id": str(request.id),
        "job_execution_id": str(job.id),
        "workflow_execution_id": str(execution.id),
        "status": execution.status,
        "last_error": execution.last_error,
    }


@router.post("/{request_id}/regenerate")
def regenerate_brd(
    request_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user_service = UserService()
    user = user_service.get_by_email(db, current_user.get("email"))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    request_service = TranscriptRequestService()
    request = request_service.get(db, request_id)
    if not request or str(request.user_id) != str(user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transcript request not found"
        )

    job_service = JobService()
    job = job_service.create(
        db,
        job_type="regenerate_brd",
        user_id=str(user.id),
        trigger_source="ui",
        trigger_event_id=None,
        arguments={"transcript_request_id": request_id},
    )

    workflow_service = WorkflowService()
    execution = workflow_service.create_execution(
        db, str(request.id), str(user.id), "UI"
    )
    job_service.set_workflow_execution_id(db, str(job.id), str(execution.id))
    job_service.set_status(db, str(job.id), "RUNNING")
    execution = workflow_service.run(db, str(execution.id))

    if execution.status == "COMPLETED":
        job_service.mark_completed(db, str(job.id))
    else:
        job_service.mark_failed(db, str(job.id))

    return {
        "request_id": str(request.id),
        "job_execution_id": str(job.id),
        "workflow_execution_id": str(execution.id),
        "status": execution.status,
        "last_error": execution.last_error,
    }
