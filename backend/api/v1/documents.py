from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..deps import get_current_user
from ...core.database import get_db
from ...modules.document.service import DocumentStore
from ...modules.user.service import UserService

router = APIRouter()


@router.get("/")

def list_documents(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user_service = UserService()
    user = user_service.get_by_email(db, current_user.get("email"))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    store = DocumentStore()
    items = store.list_by_user(db, str(user.id))
    return {"items": items}


@router.get("/by-transcript-request/{request_id}")
def get_document_by_transcript_request(
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
    store = DocumentStore()
    document = store.get_by_transcript_request_id(db, request_id)
    if not document or str(document.user_id) != str(user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


@router.get("/{document_id}")
def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user_service = UserService()
    user = user_service.get_by_email(db, current_user.get("email"))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    store = DocumentStore()
    document = store.get_by_id(db, document_id)
    if not document or str(document.user_id) != str(user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document
