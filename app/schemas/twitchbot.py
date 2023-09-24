from pydantic import BaseModel


class TimecodeAnswer(BaseModel):
    value: str


class NewElement(BaseModel):
    value: str


class UpdatedElement(BaseModel):
    id: int
    value: str


class DeletedElement(BaseModel):
    id: int


class Cheats(BaseModel):
    streamer: int | None = None
    defense: int | None = None
