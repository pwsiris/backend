from pydantic import BaseModel


class NewElement(BaseModel):
    name: str
    picture: str | None = None
    order_by: str | None = None
    description: str | None = None
    comment: str | None = None
    status: str | None = None
    type: str | None = None
    price: str | None = None
    records: str | None = None


class DeletedElement(BaseModel):
    id: int


class UpdatedElement(BaseModel):
    id: int
    name: str | None = None
    picture: str | None = None
    order_by: str | None = None
    description: str | None = None
    comment: str | None = None
    status: str | None = None
    type: str | None = None
    price: str | None = None
    records: str | None = None
