from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..deps import get_current_user
from ...core.database import get_db
from ...modules.user.service import UserService
from ...modules.transcript_request.service import TranscriptRequestService
from ...modules.workflow.schemas import WorkflowCreate
from ...modules.workflow.service import WorkflowService

router = APIRouter()


@router.post("/generate-brd")

def generate_brd(
    payload: WorkflowCreate,
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
    request = request_service.get(db, payload.transcript_request_id)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transcript request not found"
        )
    if str(request.user_id) != str(user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    workflow_service = WorkflowService()
    execution = workflow_service.create_execution(
        db, payload.transcript_request_id, str(user.id), "UI"
    )
    execution = workflow_service.run(db, str(execution.id))
    return {
        "execution_id": str(execution.id),
        "status": execution.status,
        "current_step": execution.current_step,
        "last_error": execution.last_error,
    }
