from typing import Annotated

from common.utils import check_empty
from pydantic import AfterValidator, BaseModel
from schemas._records import Records, check_records_list_order


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
    records: Annotated[
        list[Records] | None, AfterValidator(check_records_list_order)
    ] = None


class DeletedElement(BaseModel):
    id: int


class UpdatedElement(BaseModel):
    id: int
    name: Annotated[str | None, AfterValidator(check_empty)] = None
    picture: str | None = None
    picture_mode: Annotated[str | None, AfterValidator(check_empty)] = None
    order_by: str | None = None
    description: str | None = None
    comment: str | None = None
    status: str | None = None
    type: str | None = None
    price: str | None = None
    records: Annotated[
        list[Records] | None, AfterValidator(check_records_list_order)
    ] = None
