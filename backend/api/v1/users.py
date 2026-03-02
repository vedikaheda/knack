from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..deps import get_current_user
from ...core.database import get_db
from ...modules.user.schemas import SlackLinkRequest
from ...modules.user.service import UserService


router = APIRouter()


@router.post("/link-slack")
def link_slack_identity(
    payload: SlackLinkRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user_service = UserService()
    user = user_service.get_by_email(db, current_user.get("email"))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user_service.upsert_external_identity(db, str(user.id), "slack", payload.slack_user_id)
    return {"status": "ok"}
