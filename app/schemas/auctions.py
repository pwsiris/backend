from datetime import date as ddate
from typing import Annotated

from common.utils import check_empty
from pydantic import AfterValidator, BaseModel


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
    name: Annotated[str | None, AfterValidator(check_empty)] = None
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
