import logging as _logging

from sqlalchemy.pool import NullPool as _NullPoll
from sqlalchemy.ext.asyncio import AsyncSession as _Session
from sqlalchemy.ext.asyncio import create_async_engine as _create_async_engine
from sqlalchemy.ext.declarative import declarative_base as _declarative_base
from sqlalchemy.orm import sessionmaker as _sessionmaker

from config import env as _env

engine = _create_async_engine(
    _env.db_connect_url,
    echo=_env.mode != "production",
    poolclass=_NullPoll,
    pool_pre_ping=True
)
Base = _declarative_base()


AsyncSession = _sessionmaker(
    engine,  # pyright: ignore
    class_=_Session,
    expire_on_commit=False,

)


if _env.mode != "production":
    _logging.basicConfig(filename="logs/sqlalchemy/debug.log", encoding="utf-8")
    _logging.getLogger("sqlalchemy.engine").setLevel(_logging.INFO)
