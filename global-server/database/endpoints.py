"""
Database CRUDS endpoints.

All interaction with database must be procceeded here (not in models.py)
"""

import typing as _t
import sys as _sys

from sqlalchemy.ext.asyncio import AsyncSession as _AsyncSession

from . import database as _db
from . import models as _m
from .types_ import exceptions as _errors


async def get_session() -> _AsyncSession:  # pyright: ignore
    """Creates db session, yields it and closes after use"""
    async with _db.AsyncSession() as session:  # pyright: ignore
        yield session  # pyright: ignore
        session.close()


async def init_models() -> _t.NoReturn:
    """Drops all old tables and creates new from models.py"""
    async with _db.engine.begin() as conn:
        await conn.run_sync(_db.Base.metadata.drop_all)
        await conn.run_sync(_db.Base.metadata.create_all)
    await create_root()


async def create_root() -> _t.NoReturn:
    """Creates root actor"""
    async with _db.AsyncSession() as se:  # pyright: ignore
        se: _AsyncSession
        if await se.get(_m.Actor, 1):
            raise _errors.ActorExistsError("Cannot create root: Actor with id=1 already exists")
        root = _m.Actor()
        se.add(root)
        await se.commit()
        await se.refresh(root)
        if root.id != 1:
            raise _errors.ActorCreationError("Failed: root actor id != 1")
    _sys.exit(0)
