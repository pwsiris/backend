from datetime import date as ddate

from pydantic import BaseModel


class NewElement(BaseModel):
    name: str
    date: ddate | None = None
    description: str | None = None
    comment: str | None = None
    status: str | None = None
    picture: str | None = None
    order: int | None = None
    order_by: str | None = None
    auction_id: int | None = None


class UpdatedElement(BaseModel):
    id: int
    name: str | None = None
    date: ddate | None = None
    description: str | None = None
    comment: str | None = None
    status: str | None = None
    picture: str | None = None
    order: int | None = None
    order_by: str | None = None
    auction_id: int | None = None


class DeletedElement(BaseModel):
    id: int
