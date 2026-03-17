from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from ..deps import get_current_user
from ...core.config import get_settings
from ...core.database import get_db
from ...modules.auth.schemas import GoogleLoginRequest, GoogleExchangeRequest
from ...modules.auth.service import AuthService, OAuthStateError
from ...modules.user.schemas import FirefliesKeyRequest
from ...modules.user.service import UserService
from ...modules.integration.fireflies import FirefliesClient

router = APIRouter()


@router.post("/google/login")

def google_login(payload: GoogleLoginRequest, db: Session = Depends(get_db)):
    auth_service = AuthService()
    user_service = UserService()
    try:
        token_payload = auth_service.verify_id_token(payload.id_token)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {exc}"
        ) from exc
    email = token_payload.get("email")
    name = token_payload.get("name")
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email missing")
    user = user_service.get_by_email(db, email)
    if not user:
        user = user_service.create(db, email, name)
    return {"user_id": str(user.id), "email": user.email, "name": user.name}


@router.post("/google/exchange")
def google_exchange(
    payload: GoogleExchangeRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    auth_service = AuthService()
    user_service = UserService()
    tokens = auth_service.exchange_code_for_tokens(payload.code, payload.redirect_uri)
    user = user_service.get_by_email(db, current_user.get("email"))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user_service.upsert_google_tokens(db, str(user.id), tokens)
    return {"status": "ok"}


@router.get("/google/url")
def google_auth_url(purpose: str, redirect_uri: str):
    auth_service = AuthService()
    if purpose == "login":
        settings = get_settings()
        scopes = [
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
        ] + list(settings.google_docs_scopes)
        return {"auth_url": auth_service.build_auth_url(redirect_uri, scopes, state="docs")}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid purpose")


@router.get("/google/callback/login")
def google_callback_login(request: Request, code: str, db: Session = Depends(get_db)):
    auth_service = AuthService()
    user_service = UserService()
    redirect_uri = str(request.url.replace(query=""))
    id_token = auth_service.exchange_code_for_id_token(code, redirect_uri)
    token_payload = auth_service.verify_id_token(id_token)
    email = token_payload.get("email")
    name = token_payload.get("name")
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email missing")
    user = user_service.get_by_email(db, email)
    if not user:
        user = user_service.create(db, email, name)
    settings = get_settings()
    frontend_redirect = settings.google_oauth_frontend_redirect
    return RedirectResponse(
        url=f"{frontend_redirect}?id_token={id_token}&email={email}&name={name}",
        status_code=status.HTTP_302_FOUND,
    )


@router.get("/google/callback/docs")
def google_callback_docs(request: Request, code: str, state: str, db: Session = Depends(get_db)):
    auth_service = AuthService()
    user_service = UserService()
    settings = get_settings()
    redirect_uri = settings.google_oauth_callback_docs
    try:
        tokens = auth_service.exchange_code_for_tokens(code, redirect_uri, state=state)
    except OAuthStateError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    id_token = tokens.get("id_token")
    if not id_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing id_token")
    token_payload = auth_service.verify_id_token(id_token)
    email = token_payload.get("email")
    name = token_payload.get("name")
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email missing")
    user = user_service.get_by_email(db, email)
    if not user:
        user = user_service.create(db, email, name)
    user_service.upsert_google_tokens(db, str(user.id), tokens)
    settings = get_settings()
    frontend_redirect = settings.google_oauth_frontend_redirect
    return RedirectResponse(
        url=f"{frontend_redirect}?id_token={id_token}&docs=ok&email={email}",
        status_code=status.HTTP_302_FOUND,
    )


@router.post("/fireflies/connect")
def fireflies_connect(
    payload: FirefliesKeyRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user_service = UserService()
    user = user_service.get_by_email(db, current_user.get("email"))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    client = FirefliesClient(payload.api_key)
    if not client.validate_key():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Fireflies key")
    user_service.upsert_fireflies_key(db, str(user.id), payload.api_key)
    return {"status": "ok"}
