from config import env as _env
from sqlalchemy.ext.asyncio import AsyncSession as _Session
from sqlalchemy.ext.asyncio import create_async_engine as _create_async_engine
from sqlalchemy.ext.declarative import declarative_base as _declarative_base
from sqlalchemy.orm import sessionmaker as _sessionmaker


engine = _create_async_engine(_env.db_connect_url)
Base = _declarative_base()
AsyncSession = _sessionmaker(engine, class_=_Session, expire_on_commit=False)  # pyright: ignore
