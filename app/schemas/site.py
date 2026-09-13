from pydantic import BaseModel


class Message(BaseModel):
    title: str | None = None
    description: str
