from sqlalchemy.ext.asyncio import AsyncSession as _Session

from .. import database as _db
from .. import models as _m
from ..types_ import exceptions as _errors


async def init_models() -> None:
    """Drops all old tables and creates new from models.py"""
    async with _db.engine.begin() as conn:
        await conn.run_sync(_db.Base.metadata.drop_all)
        await conn.run_sync(_db.Base.metadata.create_all)


async def create_root(se: _Session) -> None:
    """Creates root actor"""
    if await se.get(_m.Actor, 1):
        raise _errors.ActorExistsError("Cannot create root: Actor with id=1 already exists")
    root = _m.Actor()
    se.add(root)
    await se.commit()
    await se.refresh(root)
    if root.id != 1:
        raise _errors.ActorCreationError("Failed: root actor id != 1")
