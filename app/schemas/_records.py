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


def check_records_list_order(value: list[Records] | None) -> list[Records] | None:
    if len(value or []) > 1:
        for element in value:
            if element.order == None:
                raise ValueError("No order in list with len >1")
    return value
