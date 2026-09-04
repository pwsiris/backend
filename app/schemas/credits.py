from typing import Annotated

from common.utils import check_empty
from pydantic import AfterValidator, BaseModel


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
    name: Annotated[str | None, AfterValidator(check_empty)] = None
    description: str | None = None
    picture: str | None = None
    picture_size: str | None = None
    picture_original: str | None = None
    creators: list[Creators] | None = None
    order: int | None = None


class DeletedElement(BaseModel):
    id: int
