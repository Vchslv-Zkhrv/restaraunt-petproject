import typing as _t
from datetime import time as _time
from datetime import date as _date
from datetime import datetime as _dt

from pydantic import BaseModel as _Base
from pydantic import Field as _Field

from . import enums as _enums


class _Schema(_Base):
    class Config:
        arbitrary_types_allowed = True
        from_attributes = True


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


class Actor(_Schema):
    id: int


class DefaultActorCreate(_Schema):
    name: str

    @property
    def abbreviation(self):
        return "da"


class DefaultActor(_Schema):
    id: int
    name: str
    actor_id: int = _Field(alias="actorId")


class UserCreate(_Schema):
    hashed_password: str = _Field(alias="hashedPassword")
    actor_id: int = _Field(alias="actorId")
    role: _enums.UserRole
    email: _t.Optional[str]
    phone: int
    telegram: _t.Optional[int]
    lname: _t.Optional[str]
    fname: str
    sname: _t.Optional[str]
    gender: bool
    birth_date: _date = _Field(alias="birthDate")
    address: _t.Optional[str]

    @property
    def abbreviation(self):
        return "da"


class UserFull(_Schema):
    hashed_password: str = _Field(alias="hashedPassword")
    actor_id: int = _Field(alias="actorId")
    role: _enums.UserRole
    email: _t.Optional[str]
    phone: int
    telegram: _t.Optional[int]
    lname: _t.Optional[str]
    fname: str
    sname: _t.Optional[str]
    gender: bool
    birth_date: _date = _Field(alias="birthDate")
    address: _t.Optional[str]
    id: int
    created: _dt
    deleted: _dt
    last_online: _dt = _Field(alias="lastOnline")


class TaskTypeCreate(_Schema):
    name: str

    @property
    def abbreviation(self):
        return "tt"


class TaskType(_Schema):
    id: int
    name: str


class TaskTypeGroupCreate(_Schema):
    name: str

    @property
    def abbreviation(self):
        return "yg"


class TaskTypeGroup(_Schema):
    id: int
    name: str


class TaskTypeGroupWithTypes(TaskTypeGroup):
    types: _t.List[TaskType]


class TaskCreate(_Schema):
    type_id: int = _Field("typeId")
    name: str
    comment: str
