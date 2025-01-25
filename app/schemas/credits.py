from pydantic import BaseModel


class Creators(BaseModel):
    name: str
    link: str | None = None
    role: str | None = None


class NewElement(BaseModel):
    name: str
    description: str | None = None
    picture: str | None = None
    picture_size: str | None = None
    picture_original: str | None = None
    creators: list[Creators] | None = None
    order: int


class UpdatedElement(BaseModel):
    id: int
    name: str | None = None
    description: str | None = None
    picture: str | None = None
    picture_size: str | None = None
    picture_original: str | None = None
    creators: list[Creators] | None = None
    order: int | None = None


class DeletedElement(BaseModel):
    id: int
