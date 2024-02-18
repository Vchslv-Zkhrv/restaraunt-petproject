"""
Database CRUDS endpoints.

All interaction with database must be procceeded here (not in models.py)
"""

from sqlalchemy.ext.asyncio import AsyncSession as _AsyncSession

from . import database as _db


async def get_session() -> _AsyncSession:  # pyright: ignore
    """Creates db session, yields it and closes after use"""
    async with _db.AsyncSession() as session:  # pyright: ignore
        yield session  # pyright: ignore
        session.close()
