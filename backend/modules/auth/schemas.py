from pydantic import BaseModel


class GoogleLoginRequest(BaseModel):
    id_token: str


class GoogleExchangeRequest(BaseModel):
    code: str
    redirect_uri: str
