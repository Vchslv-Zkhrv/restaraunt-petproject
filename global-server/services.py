import asyncio as _asyncio
import sys as _sys

import database as _db
import models as _models
from colorama import Fore as _Fore
from colorama import Style as _Style
from sqlalchemy.ext.asyncio import AsyncSession as _AsyncSession


async def get_session() -> _AsyncSession:  # pyright: ignore
    """
    creates db session, yields it and closes after use
    """
    async with _db.AsyncSession() as session:  # pyright: ignore
        yield session  # pyright: ignore


async def init_models():
    async with _db.engine.begin() as conn:
        await conn.run_sync(_db.Base.metadata.drop_all)
        await conn.run_sync(_db.Base.metadata.create_all)


async def spam():
    return _models


if __name__ == "__main__":
    if "--clean" in _sys.argv:
        print(f"{_Fore.RED}Database will be cleared{_Style.RESET_ALL}")
        if input("Are you sure? (y/n) ").lower() == "y":
            _asyncio.run(init_models())
