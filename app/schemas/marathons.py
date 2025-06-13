from datetime import date as ddate

from pydantic import BaseModel
from schemas._records import Records


class NewElement(BaseModel):
    name: str
    description: str | None = None
    comment: str | None = None
    status: str | None = None
    date_start: ddate | None = None
    date_end: ddate | None = None
    picture: str | None = None
    picture_mode: str | None = "landscape"
    rules: list[str] | None = None
    records: list[Records] | None = None
    order: int | None = None
    link: str | None = None
    marathon_id: int | None = None
    steam_id: int | None = None


class UpdatedElement(BaseModel):
    id: int
    name: str | None = None
    description: str | None = None
    comment: str | None = None
    status: str | None = None
    date_start: ddate | None = None
    date_end: ddate | None = None
    picture: str | None = None
    picture_mode: str | None = None
    rules: list[str] | None = None
    records: list[Records] | None = None
    order: int | None = None
    link: str | None = None
    marathon_id: int | None = None
    steam_id: int | None = None


class DeletedElement(BaseModel):
    id: int
