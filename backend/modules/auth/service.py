from sqlalchemy.orm import Session
from google_auth_oauthlib.flow import Flow
from ...core.config import get_settings
from ...core.security import verify_google_token, AuthError


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

    def build_auth_url(self, redirect_uri: str, scopes: list[str], state: str | None = None) -> str:
        settings = get_settings()
        client_config = {
            "web": {
                "client_id": settings.google_oauth_client_id,
                "client_secret": settings.google_oauth_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }
        flow = Flow.from_client_config(client_config, scopes=scopes, redirect_uri=redirect_uri)
        auth_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
            state=state,
        )
        return auth_url

    def exchange_code_for_tokens(self, code: str, redirect_uri: str):
        settings = get_settings()
        client_config = {
            "web": {
                "client_id": settings.google_oauth_client_id,
                "client_secret": settings.google_oauth_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }
        scopes = [
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
        ] + list(settings.google_docs_scopes)
        flow = Flow.from_client_config(client_config, scopes=scopes, redirect_uri=redirect_uri)
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
        settings = get_settings()
        client_config = {
            "web": {
                "client_id": settings.google_oauth_client_id,
                "client_secret": settings.google_oauth_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }
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
