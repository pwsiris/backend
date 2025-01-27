from pydantic import BaseModel
from schemas._records import Records


class NewElement(BaseModel):
    id: int | None = None
    name: str
    subname: str | None = None
    status: str | None = None
    genre: str | None = None
    type: str | None = None
    records: list[Records] | None = None
    comment: str | None = None
    gift_by: str | None = None
    order_by: str | None = None

    link: str | None = None
    picture: str | None = None


class DeletedElement(BaseModel):
    id: int


class UpdatedElement(BaseModel):
    id: int
    new_id: int | None = None
    name: str | None = None
    subname: str | None = None
    link: str | None = None
    picture: str | None = None
    status: str | None = None
    genre: str | None = None
    type: str | None = None
    records: list[Records] | None = None
    comment: str | None = None
    gift_by: str | None = None
    order_by: str | None = None


class UpdatedGenre(BaseModel):
    name: str
    new_name: str
