from typing import Optional
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests
from .config import get_settings


class AuthError(Exception):
    pass


def verify_google_token(id_token: str) -> Optional[dict]:
    if not id_token:
        raise AuthError("Missing id_token")
    settings = get_settings()
    try:
        payload = google_id_token.verify_oauth2_token(
            id_token,
            requests.Request(),
            settings.google_oauth_client_id,
        )
    except Exception as exc:
        raise AuthError(str(exc)) from exc
    return payload
