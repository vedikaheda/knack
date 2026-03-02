from sqlalchemy.orm import Session
from ...models.user import User
from ...models.user_integration import UserIntegration
from ...models.user_external_identity import UserExternalIdentity


class UserRepository:
    def get_by_email(self, db: Session, email: str):
        return db.query(User).filter(User.email == email).first()

    def get_by_id(self, db: Session, user_id: str):
        return db.query(User).filter(User.id == user_id).first()

    def create(self, db: Session, email: str, name: str | None):
        user = User(email=email, name=name)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def get_integration(self, db: Session, user_id: str, provider: str):
        return (
            db.query(UserIntegration)
            .filter(UserIntegration.user_id == user_id, UserIntegration.provider == provider)
            .first()
        )

    def upsert_integration(self, db: Session, user_id: str, provider: str, api_key: str):
        integration = self.get_integration(db, user_id, provider)
        if integration:
            integration.api_key = api_key
        else:
            integration = UserIntegration(user_id=user_id, provider=provider, api_key=api_key)
            db.add(integration)
        db.commit()
        db.refresh(integration)
        return integration

    def list_users_with_integration(self, db: Session, provider: str):
        return (
            db.query(User)
            .join(UserIntegration, UserIntegration.user_id == User.id)
            .filter(UserIntegration.provider == provider)
            .all()
        )

    def get_external_identity(self, db: Session, provider: str, external_user_id: str):
        return (
            db.query(UserExternalIdentity)
            .filter(
                UserExternalIdentity.provider == provider,
                UserExternalIdentity.external_user_id == external_user_id,
            )
            .first()
        )

    def upsert_external_identity(
        self, db: Session, user_id: str, provider: str, external_user_id: str
    ):
        identity = self.get_external_identity(db, provider, external_user_id)
        if identity:
            return identity
        identity = UserExternalIdentity(
            user_id=user_id, provider=provider, external_user_id=external_user_id
        )
        db.add(identity)
        db.commit()
        db.refresh(identity)
        return identity
