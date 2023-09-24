from pydantic import BaseModel


class UpdatedCreds(BaseModel):
    secrets_domain: str | None = None
    secrets_header: str | None = None
    secrets_token: str | None = None
