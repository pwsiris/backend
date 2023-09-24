from pydantic import BaseModel


class NewElement(BaseModel):
    name: str
    link: str
    icon: str
    type: str = ""
    order: int | None = None


class UpdatedElement(BaseModel):
    id: int
    name: str | None = None
    link: str | None = None
    icon: str | None = None
    type: str | None = None
    order: str | None = None


class DeletedElement(BaseModel):
    id: int
