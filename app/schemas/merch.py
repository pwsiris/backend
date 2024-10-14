from pydantic import BaseModel


class NewElement(BaseModel):
    name: str
    description: str | None = None
    price: str | None = None
    status: str | None = None
    creator_name: str | None = None
    creator_link: str | None = None
    picture: str | None = None
    picture_size: str | None = None
    order: int | None = None


class UpdatedElement(BaseModel):
    id: int
    name: str | None = None
    description: str | None = None
    price: str | None = None
    status: str | None = None
    creator_name: str | None = None
    creator_link: str | None = None
    picture: str | None = None
    picture_size: str | None = None
    order: int | None = None


class DeletedElement(BaseModel):
    id: int


class Status(BaseModel):
    status: str
