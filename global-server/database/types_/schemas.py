from datetime import time as _time

from pydantic import BaseModel as _Base
from pydantic import Field as _Field


class _Schema(_Base):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class WeekdayWorkingHours(_Schema):
    start: _time
    finish: _time


class NutritionalValues(_Schema):

    """
    Has __mul__, __add__, __sub__ mehtods.
    Can be multiplied by float and increased / decreased by NutrinionalValues
    """

    calories: float = _Field(ge=0)
    proteins: float = _Field(ge=0)
    fats: float = _Field(ge=0)
    carbohydrates: float = _Field(ge=0)

    def __mul__(self, other: float) -> "NutritionalValues":
        return NutritionalValues(
            fats=self.fats * other,
            proteins=self.proteins * other,
            calories=self.calories * other,
            carbohydrates=self.carbohydrates * other,
        )

    def __add__(self, other: "NutritionalValues") -> "NutritionalValues":
        return NutritionalValues(
            calories=self.calories + other.calories,
            proteins=self.proteins + other.proteins,
            fats=self.fats + other.fats,
            carbohydrates=self.carbohydrates + other.carbohydrates,
        )

    def __sub__(self, other: "NutritionalValues") -> "NutritionalValues":
        return NutritionalValues(
            calories=self.calories - other.calories,
            proteins=self.proteins - other.proteins,
            fats=self.fats - other.fats,
            carbohydrates=self.carbohydrates - other.carbohydrates,
        )
