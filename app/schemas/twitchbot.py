from typing import Annotated

from common.utils import check_empty
from pydantic import AfterValidator, BaseModel


class NewElement(BaseModel):
    value: Annotated[str, AfterValidator(check_empty)]


class UpdatedElement(BaseModel):
    id: int
    value: Annotated[str, AfterValidator(check_empty)]


class DeletedElement(BaseModel):
    id: int
