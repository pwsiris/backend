from datetime import datetime
from typing import Annotated

from common.utils import check_empty
from pydantic import AfterValidator, BaseModel


def round_score(value: float | None) -> float | None:
    if value == None:
        return value
    return round(value, 1)


class NewElement(BaseModel):
    id: int | None = None
    name: str
    comment: str | None = None
    voice_acting: str | None = None
    order_by: str | None = None
    series: str | None = None
    score: Annotated[float | None, AfterValidator(round_score)] = None
    status: str | None = None
    added_time: datetime | None = None
    completed_time: datetime | None = None

    link: str | None = None
    type: str | None = None
    episodes: int | None = None
    picture: str | None = None
    picture_mode: str | None = "portrait"


class DeletedElement(BaseModel):
    id: int


class UpdatedElement(BaseModel):
    id: int
    new_id: int | None = None
    name: Annotated[str | None, AfterValidator(check_empty)] = None
    link: str | None = None
    comment: str | None = None
    voice_acting: str | None = None
    order_by: str | None = None
    series: str | None = None
    type: str | None = None
    episodes: int | None = None
    picture: str | None = None
    picture_mode: Annotated[str | None, AfterValidator(check_empty)] = None
    score: Annotated[float | None, AfterValidator(round_score)] = None
    status: str | None = None
    added_time: datetime | None = None
    completed_time: datetime | None = None
