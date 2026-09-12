from typing import Annotated

from common.utils import check_empty
from pydantic import AfterValidator, BaseModel


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
    name: Annotated[str | None, AfterValidator(check_empty)] = None
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
