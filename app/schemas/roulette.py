from typing import Annotated

from common.utils import check_empty
from pydantic import AfterValidator, BaseModel


class NewElement(BaseModel):
    name: str
    rarity: str
    description: str | None = None


class UpdatedElement(BaseModel):
    id: int
    name: Annotated[str | None, AfterValidator(check_empty)] = None
    rarity: Annotated[str | None, AfterValidator(check_empty)] = None
    description: str | None = None


class DeletedElement(BaseModel):
    id: int
