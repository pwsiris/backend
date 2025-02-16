from pydantic import BaseModel


class Message(BaseModel):
    title: str | None = None
    description: str


class Title(BaseModel):
    text: str
    visible: bool
    editable: bool


class Enabled(BaseModel):
    value: bool
