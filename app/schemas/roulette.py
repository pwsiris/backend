from pydantic import BaseModel


class NewElement(BaseModel):
    name: str
    rarity: str
    description: str | None = None


class UpdatedElement(BaseModel):
    id: int
    name: str | None = None
    rarity: str | None = None
    description: str | None = None


class DeletedElement(BaseModel):
    id: int
