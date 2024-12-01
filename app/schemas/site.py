from pydantic import BaseModel


class Message(BaseModel):
    title: str | None = None
    description: str


class Title(BaseModel):
    text: str
    editable: bool


class Enabled(BaseModel):
    value: bool
