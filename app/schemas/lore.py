from pydantic import BaseModel


class NewElement(BaseModel):
    text: str
    block_id: str
    order: int | None = None


class UpdatedElement(BaseModel):
    id: int
    text: str | None = None
    block_id: str | None = None
    order: int | None = None


class DeletedElement(BaseModel):
    id: int
