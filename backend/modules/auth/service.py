import threading
import time
import uuid

from sqlalchemy.orm import Session
from google_auth_oauthlib.flow import Flow
from ...core.config import get_settings
from ...core.security import verify_google_token, AuthError


class OAuthStateError(AuthError):
    pass


_OAUTH_STATE_TTL_SECONDS = 600
_oauth_state_store: dict[str, dict[str, float | str]] = {}
_oauth_state_lock = threading.Lock()


class AuthService:
    def verify_request(self, db: Session, authorization: str):
        token = authorization.replace("Bearer ", "") if authorization else ""
        try:
            return verify_google_token(token)
        except AuthError:
            return None

    def verify_id_token(self, id_token: str):
        return verify_google_token(id_token)

    def verify_service_token(self, token: str) -> bool:
        settings = get_settings()
        return token == settings.clawdbot_service_token

    def _build_client_config(self) -> dict:
        settings = get_settings()
        return {
            "web": {
                "client_id": settings.google_oauth_client_id,
                "client_secret": settings.google_oauth_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }

    def _cleanup_oauth_states(self) -> None:
        now = time.time()
        expired_states = [
            state
            for state, payload in _oauth_state_store.items()
            if float(payload["expires_at"]) <= now
        ]
        for state in expired_states:
            _oauth_state_store.pop(state, None)

    def build_auth_url(self, redirect_uri: str, scopes: list[str], state: str | None = None) -> str:
        client_config = self._build_client_config()
        flow = Flow.from_client_config(client_config, scopes=scopes, redirect_uri=redirect_uri)
        resolved_state = state or uuid.uuid4().hex
        auth_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
            state=resolved_state,
        )
        code_verifier = flow.code_verifier
        if not code_verifier:
            raise AuthError("Google OAuth code verifier was not created")
        with _oauth_state_lock:
            self._cleanup_oauth_states()
            _oauth_state_store[resolved_state] = {
                "code_verifier": code_verifier,
                "expires_at": time.time() + _OAUTH_STATE_TTL_SECONDS,
            }
        return auth_url

    def _pop_code_verifier(self, state: str) -> str:
        with _oauth_state_lock:
            self._cleanup_oauth_states()
            payload = _oauth_state_store.pop(state, None)
        if not payload:
            raise OAuthStateError("Google OAuth session expired or is invalid. Please try signing in again.")
        return str(payload["code_verifier"])

    def exchange_code_for_tokens(self, code: str, redirect_uri: str, state: str | None = None):
        settings = get_settings()
        client_config = self._build_client_config()
        scopes = [
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
        ] + list(settings.google_docs_scopes)
        flow = Flow.from_client_config(client_config, scopes=scopes, redirect_uri=redirect_uri)
        if state:
            flow.code_verifier = self._pop_code_verifier(state)
        flow.fetch_token(code=code)
        credentials = flow.credentials
        return {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": list(credentials.scopes or []),
            "id_token": credentials.id_token,
        }

    def exchange_code_for_id_token(self, code: str, redirect_uri: str) -> str:
        client_config = self._build_client_config()
        scopes = [
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
        ]
        flow = Flow.from_client_config(client_config, scopes=scopes, redirect_uri=redirect_uri)
        flow.fetch_token(code=code)
        credentials = flow.credentials
        if not credentials or not credentials.id_token:
            raise AuthError("No id_token returned")
        return credentials.id_token
