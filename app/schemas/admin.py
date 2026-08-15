from pydantic import BaseModel


class Token(BaseModel):
    token: str


class UpdatedCreds(BaseModel):
    secrets_domain: str | None = None
    secrets_header: str | None = None
    secrets_token: str | None = None
