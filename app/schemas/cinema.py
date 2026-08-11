from datetime import date as ddate
from typing import Annotated

from pydantic import AfterValidator, BaseModel


def is_empty(value: str | None) -> str | None:
    if value == "":
        raise ValueError("Can't be empty string")
    return value


class NewElement(BaseModel):
    name: str
    subname: str | None = None
    type: str
    event: str | None = None
    comment: str | None = None
    date: ddate | None = None
    status: str | None = None
    order_by: str | None = None


class DeletedElement(BaseModel):
    id: int


class UpdatedElement(BaseModel):
    id: int
    name: Annotated[str | None, AfterValidator(is_empty)] = None
    subname: str | None = None
    type: Annotated[str | None, AfterValidator(is_empty)] = None
    event: str | None = None
    comment: str | None = None
    date: ddate | None = None
    status: str | None = None
    order_by: str | None = None
