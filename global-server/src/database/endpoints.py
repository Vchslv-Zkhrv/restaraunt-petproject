"""
Database base CRUD endpoints.
"""
from sqlalchemy.ext.asyncio import AsyncSession as _Session

from . import database as _db
from . import models as _models


async def get_session() -> _Session:  # pyright: ignore
    """Creates db session, yields it and closes after use"""
    async with _db.AsyncSession() as session:  # pyright: ignore
        yield session  # pyright: ignore
        session.close()


async def _create_model[T: _models.model](se: _Session, model: T) -> T:
    se.add(model)
    await se.commit()
    await se.refresh(model)
    return model
