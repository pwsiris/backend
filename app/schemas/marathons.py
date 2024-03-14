from pydantic import BaseModel


class NewElement(BaseModel):
    name: str
    description: str | None = None
    comment: str | None = None
    status: str | None = None
    picture: str | None = None
    records: str | None = None
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
    picture: str | None = None
    records: str | None = None
    order: int | None = None
    link: str | None = None
    marathon_id: int | None = None
    steam_id: int | None = None


class DeletedElement(BaseModel):
    id: int
