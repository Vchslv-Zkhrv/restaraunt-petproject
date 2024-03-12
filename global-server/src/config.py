import typing as _t

from pydantic_settings import BaseSettings as _BaseSettings
from pydantic_settings import SettingsConfigDict as _SettingsConfigDict


PHONE_VALIDATION_REGEX = r"9\d\d\d\d\d\d\d\d\d"
MAX_EXPIERENCE_COEFFICIENT = 1.5
DOTENV_PATH = ".env"
CUSTOMER_MINIMAL_AGE = 12  # 12+, customers under this age will not be able to register


class Settings(_BaseSettings):

    MODE: _t.Literal["dev", "test", "production"]
    DB_CONNECT_URL: str
    PASSWORD_SALT: str

    model_config = _SettingsConfigDict(env_file=".env")


settings = Settings()  # pyright: ignore
