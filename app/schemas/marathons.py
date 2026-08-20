from datetime import date as ddate
from typing import Annotated

from pydantic import AfterValidator, BaseModel
from schemas._records import Records, check_records_list_order


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
    records: Annotated[
        list[Records] | None, AfterValidator(check_records_list_order)
    ] = None
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
    records: Annotated[
        list[Records] | None, AfterValidator(check_records_list_order)
    ] = None
    order: int | None = None
    link: str | None = None
    marathon_id: int | None = None
    steam_id: int | None = None


class DeletedElement(BaseModel):
    id: int
