import typing as _t
import sys as _sys

from sqlalchemy.ext.asyncio import AsyncSession as _Session

from .. import database as _db
from .. import endpoints as _crud
from .. import models as _models
from . import reset as _reset
from . import general as _general


async def _create_task_types_groups(se: _Session) -> None:
    for name in (
        "task operating",
        "order handling",
        "item operating",
        "user operating",
        "warehouse operations"
    ):
        await _crud.create_model(_models.TaskTypeGroup(name=name), se)


async def _create_task_types(se: _Session) -> None:
    await _general.create_task_type("task creation", ["task operating"], se)
    await _general.create_task_type("task deletion", ["task operating"], se)
    await _general.create_task_type("task access", ["task operating"], se)
    await _general.create_task_type("task inspection", ["task operating"], se)
    await _general.create_task_type("task modification", ["task operating"], se)
    await _general.create_task_type("task execution", ["task operating"], se)
    await _general.create_task_type("user register", ["user operating"], se)
    await _general.create_task_type("user deletion", ["user operating"], se)
    await _general.create_task_type("user role change", ["user operating"], se)
    await _general.create_task_type("order creation", ["order handling"], se)
    await _general.create_task_type("order delegation", ["order handling"], se)
    await _general.create_task_type("order payment", ["order handling", "financial operations"], se)
    await _general.create_task_type("order cooking", ["order handling"], se)
    await _general.create_task_type("order packaging", ["order handilg"], se)
    await _general.create_task_type("order delivery", ["order handilg"], se)
    await _general.create_task_type("item register", ["item operating"], se)
    await _general.create_task_type("item writoff", ["item operating", "warehouse operations"], se)
    await _general.create_task_type("item order", ["item operating", "warehouse operations"], se)
    await _general.create_task_type("item supply", ["item operating", "warehouse operations"], se)
    await _general.create_task_type("item movement", ["item operating", "warehouse operations"], se)


async def generate_default_data() -> _t.NoReturn:

    # drop all tables and create new ones
    await _reset.init_models()

    async with _db.AsyncSession() as se:  # pyright: ignore
        se: _Session

        await _reset.create_root(se)
        await _general.create_default_actor("SYSTEM", se)
        await _create_task_types_groups(se)
        await _create_task_types(se)

    _sys.exit(0)
