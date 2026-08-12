from typing import Annotated

from pydantic import AfterValidator, BaseModel
from schemas._records import Records, check_records_list_order


class NewElement(BaseModel):
    id: int | None = None
    name: str
    subname: str | None = None
    status: str | None = None
    genre: str | None = None
    type: str | None = None
    records: Annotated[
        list[Records] | None, AfterValidator(check_records_list_order)
    ] = None
    comment: str | None = None
    gift_by: str | None = None
    order_by: str | None = None
    link: str | None = None
    picture: str | None = None
    picture_mode: str | None = "landscape"


class DeletedElement(BaseModel):
    id: int


class UpdatedElement(BaseModel):
    id: int
    new_id: int | None = None
    name: str | None = None
    subname: str | None = None
    link: str | None = None
    picture: str | None = None
    picture_mode: str | None = None
    status: str | None = None
    genre: str | None = None
    type: str | None = None
    records: Annotated[
        list[Records] | None, AfterValidator(check_records_list_order)
    ] = None
    comment: str | None = None
    gift_by: str | None = None
    order_by: str | None = None


class UpdatedGenre(BaseModel):
    name: str
    new_name: str
