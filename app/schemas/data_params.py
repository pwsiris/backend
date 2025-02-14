from pydantic import BaseModel, ValidationError, model_validator
from typing_extensions import Self


class Element(BaseModel):
    name: str
    value_bool: bool | None = None
    value_int: int | None = None
    value_float: float | None = None
    value_str: str | None = None

    @model_validator(mode="after")
    def only_one_value(self) -> Self:
        count = 0
        for value in ("value_bool", "value_int", "value_float", "value_str"):
            if getattr(self, value) != None:
                count += 1

        if count == 0:
            raise ValidationError("Need one value")
        if count > 1:
            raise ValidationError("Need only one value")
        return self


class ElementName(BaseModel):
    name: str
