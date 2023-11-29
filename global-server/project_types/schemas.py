from datetime import time as _time

from pydantic import BaseModel as _Base


class _Schema(_Base):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class WeekdayWorkingHours(_Schema):
    start: _time
    finish: _time


class NutritionalValues(_Schema):

    """
    Has __mul__ and __add__ mehtods.
    Can be multiplied by float and increased by NutrinionalValues
    """

    calories: float
    proteins: float
    fats: float
    carbohydrates: float

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
