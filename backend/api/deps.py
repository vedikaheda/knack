from fastapi import Depends, Header
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..modules.auth.service import AuthService


def get_auth_service() -> AuthService:
    return AuthService()


def get_current_user(
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None),
    auth_service: AuthService = Depends(get_auth_service),
):
    if not authorization:
        return None
    return auth_service.verify_request(db=db, authorization=authorization)
