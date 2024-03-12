import typing as _t
from datetime import datetime as _dt

from sqlalchemy.ext.asyncio import AsyncSession as _Session
import sqlalchemy as _sql

from src.database import models as _models
from src.database import endpoints as _crud
from src.database import database as _db
from src.database import types_ as _dbtypes


"""
This module contains CRUDs that creates general data necessary for all project implementations.

These CRUD endpoints must not appear in database/endpoints.py because they will never be used in runtime.
"""


async def init_models() -> None:
    """Drops all old tables and creates new from models.py"""
    async with _db.engine.begin() as conn:
        await conn.run_sync(_db.Base.metadata.drop_all)
        await conn.run_sync(_db.Base.metadata.create_all)


async def create_root(se: _Session) -> None:
    """Creates root actor"""
    if await se.get(_models.Actor, 1):
        raise _dbtypes.exceptions.ActorExistsError("Cannot create root: Actor with id=1 already exists")
    root = await _crud._create_model(se, _models.Actor())
    if root.id != 1:
        raise _dbtypes.exceptions.ActorCreationError("Failed: root actor id != 1")


async def create_system_da(
    se: _Session
) -> _models.DefaultActor:

    """
    Creates the SYSTEM DefaultActor and grants all access rights to it bypassing security restrictions
    """

    grant_rights_type_id = (await se.execute(
        _sql
        .select(_models.TaskType.id)
        .where(_models.TaskType.name == "grant actor rights")
    )).one()._tuple()[0]

    actor = await _crud._create_model(se, _models.Actor())
    da = await _crud._create_model(se, _models.DefaultActor(actor_id=actor.id, name="SYSTEM"))

    types_ids = await se.stream(_sql.select(_models.TaskType.id))
    async for tid in types_ids:
        tid = tid._tuple()[0]
        for role in _dbtypes.enums.AccessRole:
            target = await _crud._create_model(se, _models.TaskTarget())
            await _crud._create_model(
                se,
                _models.ActorAccessLevel(
                    actor_id=actor.id,
                    task_type_id=tid,
                    task_target_id=target.id,
                    role=role
                )
            )
            now = _dt.utcnow()
            await _crud._create_model(
                se,
                _models.Task(
                    type_id=grant_rights_type_id,
                    name="Grant SYSTEM access rights",
                    comment="deployment",
                    status=_dbtypes.enums.TaskStatus.executed,
                    target_id=target.id,
                    author_id=1,
                    executor_id=2,
                    inspector_id=1,
                    created=now,
                    execution_started=now,
                    completed=now,
                    approved=now
                )
            )

    return da


async def create_task_type_group(
    name: str,
    se: _Session
) -> _models.TaskTypeGroup:

    return await _crud._create_model(se, _models.TaskTypeGroup(name=name))


async def create_task_type(
    name: str,
    groups_names: _t.List[str],
    se: _Session
) -> _models.TaskType:

    task_type = await _crud._create_model(se, _models.TaskType(name=name))
    groups_ids = await se.stream(
        _sql
        .select(_models.TaskTypeGroup.id)
        .where(_models.TaskTypeGroup.name.in_(groups_names))
    )
    async for row in groups_ids:
        await _crud._create_model(se, _models.TaskTypeGroupType(type_id=task_type.id, group_id=row[0]))

    await se.refresh(task_type)
    return task_type
