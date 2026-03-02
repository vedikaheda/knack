import json
from sqlalchemy.orm import Session
from ...core.encryption import encrypt_value, decrypt_value
from .repository import UserRepository


class UserService:
    def __init__(self) -> None:
        self.repo = UserRepository()

    def get_by_email(self, db: Session, email: str):
        return self.repo.get_by_email(db, email)

    def get_by_id(self, db: Session, user_id: str):
        return self.repo.get_by_id(db, user_id)

    def create(self, db: Session, email: str, name: str | None):
        return self.repo.create(db, email, name)

    def upsert_fireflies_key(self, db: Session, user_id: str, api_key: str):
        encrypted = encrypt_value(api_key)
        return self.repo.upsert_integration(db, user_id, "fireflies", encrypted)

    def get_fireflies_key(self, db: Session, user_id: str) -> str | None:
        integration = self.repo.get_integration(db, user_id, "fireflies")
        if not integration:
            return None
        return decrypt_value(integration.api_key)

    def upsert_google_tokens(self, db: Session, user_id: str, tokens: dict):
        encrypted = encrypt_value(json.dumps(tokens))
        return self.repo.upsert_integration(db, user_id, "google", encrypted)

    def get_google_tokens(self, db: Session, user_id: str) -> dict | None:
        integration = self.repo.get_integration(db, user_id, "google")
        if not integration:
            return None
        return json.loads(decrypt_value(integration.api_key))

    def list_users_with_google(self, db: Session):
        return self.repo.list_users_with_integration(db, "google")

    def get_by_external_identity(self, db: Session, provider: str, external_user_id: str):
        identity = self.repo.get_external_identity(db, provider, external_user_id)
        if not identity:
            return None
        return self.repo.get_by_id(db, str(identity.user_id))

    def upsert_external_identity(self, db: Session, user_id: str, provider: str, external_user_id: str):
        return self.repo.upsert_external_identity(db, user_id, provider, external_user_id)
