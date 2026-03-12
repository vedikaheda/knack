from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "dev"
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/brd"
    encryption_key: str = "CHANGE_ME"
    google_oauth_client_id: str = ""
    google_oauth_client_secret: str = ""
    google_docs_scopes: list[str] = ["https://www.googleapis.com/auth/documents"]
    google_oauth_frontend_redirect: str = "http://localhost:8501"
    google_oauth_callback_docs: str = "http://localhost:8000/api/v1/auth/google/callback/docs"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    clawdbot_service_token: str = "CHANGE_ME"
    openclaw_hooks_url: str = ""
    openclaw_hooks_token: str = "CHANGE_ME"

    class Config:
        env_file = "backend/.env"
        env_file_encoding = "utf-8"
        extra= "allow"


@lru_cache

def get_settings() -> Settings:
    return Settings()
