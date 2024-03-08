import typing as _t

from sqlalchemy.ext.asyncio import AsyncSession as _Session
import sqlalchemy as _sql

from database import models as _models
from database import endpoints as _crud


"""
This module contains CRUDs that creates general data necessary for all project implementations.

These CRUD endpoints must not appear in database/endpoints.py because they will never be used in runtime.
"""


async def create_default_actor(
    name: str,
    se: _Session
) -> _models.DefaultActor:

    actor = await _crud.create_model(_models.Actor(), se)
    return await _crud.create_model(_models.DefaultActor(actor_id=actor.id, name=name), se)


async def create_task_type_group(
    name: str,
    se: _Session
) -> _models.TaskTypeGroup:

    return await _crud.create_model(_models.TaskTypeGroup(name=name), se)


async def create_task_type(
    name: str,
    groups_names: _t.List[str],
    se: _Session
) -> _models.TaskType:

    task_type = await _crud.create_model(_models.TaskType(name=name), se)
    groups_ids = await se.stream(
        _sql
        .select(_models.TaskTypeGroup.id)
        .where(_models.TaskTypeGroup.name.in_(groups_names))
    )
    async for row in groups_ids:
        await _crud.create_model(_models.TaskTypeGroupType(type_id=task_type.id, group_id=row[0]), se)

    await se.refresh(task_type)
    return task_type
