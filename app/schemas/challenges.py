from pydantic import BaseModel
from schemas._records import Records


class NewElement(BaseModel):
    name: str
    picture: str | None = None
    picture_mode: str | None = "landscape"
    order_by: str | None = None
    description: str | None = None
    comment: str | None = None
    status: str | None = None
    type: str | None = None
    price: str | None = None
    records: list[Records] | None = None


class DeletedElement(BaseModel):
    id: int


class UpdatedElement(BaseModel):
    id: int
    name: str | None = None
    picture: str | None = None
    picture_mode: str | None = None
    order_by: str | None = None
    description: str | None = None
    comment: str | None = None
    status: str | None = None
    type: str | None = None
    price: str | None = None
    records: list[Records] | None = None
