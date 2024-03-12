import pytest

from sqlalchemy.ext.asyncio import AsyncSession
from passlib import hash

from src.database import database
from src.config import settings


@pytest.fixture()
async def session():
    async with database.AsyncSession() as session:  # pyright: ignore
        session: AsyncSession
        yield session


@pytest.fixture()
async def password():
    return hash.bcrypt.hash(f"password{settings.PASSWORD_SALT}")
