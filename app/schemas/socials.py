from typing import Annotated

from common.utils import check_empty
from pydantic import AfterValidator, BaseModel


class NewElement(BaseModel):
    name: str
    link: str
    icon: str
    type: str = ""
    order: int | None = None


class UpdatedElement(BaseModel):
    id: int
    name: Annotated[str | None, AfterValidator(check_empty)] = None
    link: Annotated[str | None, AfterValidator(check_empty)] = None
    icon: Annotated[str | None, AfterValidator(check_empty)] = None
    type: str | None = None
    order: int | None = None


class DeletedElement(BaseModel):
    id: int
