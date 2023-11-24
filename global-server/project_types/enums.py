from enum import Enum as _Enum


class Weekday(_Enum):

    """
    type hint for sqlalchemy models
    """

    sunday = 0
    monday = 1
    tuesday = 2
    wednesday = 3
    thursday = 4
    friday = 5
    saturday = 6
