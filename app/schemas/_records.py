from pydantic import BaseModel, model_validator
from typing_extensions import Self


class Records(BaseModel):
    name: str
    url: str
    order: int | None = None

    @model_validator(mode="after")
    def exclude_order(self) -> Self:
        if self.order == None:
            del self.order
        return self
