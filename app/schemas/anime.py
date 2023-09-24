from datetime import datetime

from pydantic import BaseModel


class NewElement(BaseModel):
    id: int | None = None
    name: str
    comment: str | None = None
    voice_acting: str | None = None
    order_by: str
    series: str | None = None
    score: int | None = None
    status: str | None = None
    added_time: datetime | None = None
    completed_time: datetime | None = None

    link: str | None = None
    type: str | None = None
    episodes: int | None = None
    picture: str | None = None


class DeletedElement(BaseModel):
    id: int


class UpdatedElement(BaseModel):
    id: int
    new_id: int | None = None
    name: str | None = None
    link: str | None = None
    comment: str | None = None
    voice_acting: str | None = None
    order_by: str | None = None
    series: str | None = None
    type: str | None = None
    episodes: int | None = None
    picture: str | None = None
    score: int | None = None
    status: str | None = None
    added_time: datetime | None = None
    completed_time: datetime | None = None
