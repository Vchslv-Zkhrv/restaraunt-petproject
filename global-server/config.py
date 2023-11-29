from dotenv import dotenv_values as _values
from pydantic import BaseModel as _BM
from pydantic import Field as _Field


PHONE_VALIDATION_REGEX = r"9\d\d\d\d\d\d\d\d\d"
MAX_EXPIERENCE_COEFFICIENT = 1.5


class Environment(_BM):
    db_connect_url: str = _Field(alias="DB_CONNECT_URL")


env = Environment(**_values(".env"))  # pyright: ignore
