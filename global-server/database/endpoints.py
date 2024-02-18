"""
Database CRUDS endpoints.

All interaction with database must be procceeded here (not in models.py)
"""

from sqlalchemy.ext.asyncio import AsyncSession as _AsyncSession

from . import database as _db
from . import models as _models


async def get_session() -> _AsyncSession:  # pyright: ignore
    """Creates db session, yields it and closes after use"""
    async with _db.AsyncSession() as session:  # pyright: ignore
        yield session  # pyright: ignore


async def init_models():
    """Drops all old tables and creates new from models.py"""
    async with _db.engine.begin() as conn:
        await conn.run_sync(_db.Base.metadata.drop_all)
        await conn.run_sync(_db.Base.metadata.create_all)


async def spam():
    return _models
