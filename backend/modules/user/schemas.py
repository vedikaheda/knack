from pydantic import BaseModel


class UserCreate(BaseModel):
    email: str
    name: str | None = None


class FirefliesKeyRequest(BaseModel):
    api_key: str


class SlackLinkRequest(BaseModel):
    slack_user_id: str
