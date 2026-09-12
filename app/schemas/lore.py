from typing import Annotated

from common.utils import check_empty
from pydantic import AfterValidator, BaseModel


class NewElement(BaseModel):
    text: str
    block_id: str
    order: int | None = None


class UpdatedElement(BaseModel):
    id: int
    text: Annotated[str | None, AfterValidator(check_empty)] = None
    block_id: Annotated[str | None, AfterValidator(check_empty)] = None
    order: int | None = None


class DeletedElement(BaseModel):
    id: int
