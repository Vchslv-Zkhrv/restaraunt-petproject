# file is ignored by the Black formatter but still meets the flake8 rules
# it was made to improve readability


"""
Module containing (only) sqlalchemy models.

"""


import operator as _operator
import re as _re
import typing as _t
from datetime import date as _date
from datetime import datetime as _dt
from datetime import time as _time

import config as _cfg
import passlib.hash as _hash
import sqlalchemy as _sql
import sqlalchemy.orm as _orm
import sqlalchemy.schema as _schema
from email_validator import EmailNotValidError as _EmailError
from email_validator import validate_email as _validate_email
from typeguard import check_type as _check_type

from . import types_ as _types
from .database import Base as _Base


_T = _t.TypeVar("_T")
_comprasion = _t.Literal["eq", "ne", "gt", "ge", "lt", "le"]


def _check_value(value: object, value_name: str, criterion: object, comprasion: _comprasion):
    """
    Raises ValueError if value don't meet criterion
    """
    method, compr = {
        "eq": (_operator.eq, "equals to"),
        "ne": (_operator.ne, "not equals to"),
        "lt": (_operator.lt, "lower than"),
        "le": (_operator.le, "lower than or equals to"),
        "gt": (_operator.gt, "greater than"),
        "ge": (_operator.ge, "greater than or equals to"),
    }[comprasion]
    if not method(value, criterion):
        raise ValueError(f"{value_name} must be {compr} {criterion}")


class Actor(_Base):
    __tablename__ = "Actor"

    """
    Basic model for both real and virtual actors
    """

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )

    # relationships

    created_tasks: _orm.Mapped[
        _t.List["Task"]] = _orm.relationship(back_populates="author")

    tasks_to_execute: _orm.Mapped[
        _t.List["Task"]] = _orm.relationship(back_populates="executor")

    tasks_to_inspect: _orm.Mapped[
        _t.List["Task"]] = _orm.relationship(back_populates="inspector")

    default_actor: _orm.Mapped[
        _t.Optional["DefaultActor"]] = _orm.relationship(back_populates="actor")

    user: _orm.Mapped[
        _t.Optional["User"]] = _orm.relationship(back_populates="actor")

    personal_access_levels: _orm.Mapped[
        _t.List["ActorAccessLevel"]] = _orm.relationship(back_populates="actor")


class Restaurant(_Base):
    __tablename__ = "Restaurant"

    """
    Model describing a restaurant and it's local server
    """

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    default_actor_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("DefaultActor.id"),
        nullable=False,
        unique=True,
        index=True,
    )
    url: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        nullable=False,
        unique=True,
        index=True
    )
    address: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        nullable=False,
        unique=True,
        index=True
    )
    accepts_online_orders: _orm.Mapped[bool] = _orm.mapped_column(
        _sql.Boolean,
        nullable=False,
        index=True
    )

    # relationships

    default_actor: _orm.Mapped[
        "DefaultActor"] = _orm.relationship(back_populates="restaurant")

    external_departments: _orm.Mapped[
        _t.List["RestaurantExternalDepartment"]] = _orm.relationship(back_populates="restaurant")

    internal_departments: _orm.Mapped[
        _t.List["RestaurantInternalDepartment"]] = _orm.relationship(back_populates="restaraunt")

    employees: _orm.Mapped[
        _t.List["RestaurantEmployee"]] = _orm.relationship(back_populates="restaurant")

    stock_balance: _orm.Mapped[
        _t.List["MaterialStockBalance"]] = _orm.relationship(back_populates="restaurant")

    products: _orm.Mapped[
        _t.List["RestaurantProduct"]] = _orm.relationship(back_populates="restaurant")

    customer_orders: _orm.Mapped[
        _t.List["CustomerOrder"]] = _orm.relationship(back_populates="restaurant")

    table_locations: _orm.Mapped[
        _t.List["TableLocation"]] = _orm.relationship(back_populates="restaurant")

    discounts: _orm.Mapped[
        _t.List["RestaurantDiscount"]] = _orm.relationship(back_populates="restaurant")


class RestaurantExternalDepartment(_Base):
    __tablename__ = "RestaurantExternalDepartment"

    """
    Restaurant department that issues orders
    (hall / pickup service / drive-thru / delivery)
    """

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    default_actor_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("DefaultActor.id"),
        nullable=False,
        index=True,
    )
    restaurant_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Restaurant.id"),
        index=True,
        nullable=False,
    )
    type: _orm.Mapped[_types.enums.RestarauntExternalDepartmentType] = _orm.mapped_column(
        _sql.Enum(_types.enums.RestarauntExternalDepartmentType),
        nullable=False,
        index=True,
    )

    # relationships

    restaurant: _orm.Mapped[
        "Restaurant"] = _orm.relationship(back_populates="external_departments")

    working_hours: _orm.Mapped[
        _t.List["RestaurantExternalDepartmentWorkingHours"]] = _orm.relationship(back_populates="department")

    default_actor: _orm.Mapped[
        "DefaultActor"] = _orm.relationship(back_populates="restaurant_external_department")

    # properties

    @property
    def working_hours_tuple(
        self,
    ) -> _t.Tuple[_types.schemas.WeekdayWorkingHours]:
        return tuple(
            _types.schemas.WeekdayWorkingHours.model_validate(h)
            for h in sorted(self.working_hours, key=_operator.attrgetter("weekday"))
        )  # pyright: ignore

    @property
    def working_hours_dict(
        self,
    ) -> _t.Dict[_types.enums.Weekday, _types.schemas.WeekdayWorkingHours]:
        return {k: v for k, v in ((_types.enums.Weekday(i), w) for i, w in enumerate(self.working_hours_tuple))}


class RestaurantExternalDepartmentWorkingHours(_Base):
    __tablename__ = "RestaurantExternalDepartmentWorkingHours"

    """
    Restaurant external department working hours at a weekday
    """

    # columns
    department_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("RestaurantExternalDepartment.id"),
        primary_key=True,
    )
    weekday: _orm.Mapped[_types.enums.Weekday] = _orm.mapped_column(
        _sql.Enum(_types.enums.Weekday),
        primary_key=True
    )
    start: _orm.Mapped[_time] = _orm.mapped_column(
        _sql.Time,
        nullable=False,
        index=True
    )
    finish: _orm.Mapped[_time] = _orm.mapped_column(
        _sql.Time,
        nullable=False,
        index=True
    )

    # relationships

    department: _orm.Mapped[
        "RestaurantExternalDepartment"] = _orm.relationship(back_populates="working_hours")

    # composite primary key
    __table_args__ = (_schema.PrimaryKeyConstraint(department_id, weekday), {})


class RestaurantInternalDepartment(_Base):
    __tablename__ = "RestaurantInternalDepartment"

    """
    Restaurant department not involved in issuing orders
    """

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    name: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        nullable=False,
        index=True
    )
    default_actor_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("DefaultActor.id"),
        nullable=False,
        index=True,
    )
    restaurant_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Restaurant.id"),
        index=True,
        nullable=False,
    )
    type: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        nullable=False,
        index=True
    )

    # relationships

    restaurant: _orm.Mapped[
        "Restaurant"] = _orm.relationship(back_populates="internal_departments")

    default_actor: _orm.Mapped[
        "DefaultActor"] = _orm.relationship(back_populates="restaurant_internal_department")

    sub_departments: _orm.Mapped[
        _t.List["RestaurantInternalSubDepartment"]] = _orm.relationship(back_populates="parent")

    parent_department: _orm.Mapped[
        "RestaurantInternalSubDepartment"] = _orm.relationship(back_populates="child")


class RestaurantInternalSubDepartment(_Base):
    __tablename__ = "RestaurantInternalSubDepartment"

    """
    Internal restaraunt department that reports to a parent department
    """

    # columns
    parent_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("RestaurantInternalDepartment.id"),
        primary_key=True,
    )
    child_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("RestaurantInternalDepartment.id"),
        primary_key=True,
    )

    # relationships

    parent: _orm.Mapped[
        "RestaurantInternalDepartment"] = _orm.relationship(back_populates="sub_departments")

    child: _orm.Mapped[
        "RestaurantInternalDepartment"] = _orm.relationship(back_populates="parent_department")

    # composite primary key
    __table_args__ = (_schema.PrimaryKeyConstraint(child_id, parent_id), {})


class DefaultActorTaskDelegation(_Base):
    __tablename__ = "DefaultActorTaskDelegation"

    """
    Logic for processing tasks and distributing subtasks to delegates.

    filter(<filter_>, <source>)
    must return a generator of attachments that will be distributed to delegate

    Returned values must be instances of <result_type> model class.
    filter_ can use only python built-ins.
    source must be a string that starts with 'self.'
    """

    @_orm.reconstructor
    def _set_result_type(self):
        self.attachments_type = globals()[self.attachments_type_name]

    # columns
    default_actor_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("DefaultActor.id"),
        primary_key=True
    )
    incoming_task_type_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("TaskType.id"),
        primary_key=True
    )
    outcoming_task_type_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("TaskType.id"),
        primary_key=True
    )

    # columns with python code that
    # must be used to collect delegation attachments
    source: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        nullable=False
    )
    filter_: _orm.Mapped[_t.Optional[str]] = _orm.mapped_column(
        _sql.String,
        nullable=True
    )
    attachments_type_name: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        nullable=False
    )

    # columns for Task creation
    task_name: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        nullable=False
    )
    task_comment: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String
    )
    task_start_execution: _orm.Mapped[_dt] = _orm.mapped_column(
        _sql.DateTime,
        index=True
    )
    task_fail_on_late_start: _orm.Mapped[bool] = _orm.mapped_column(
        _sql.Boolean,
        nullable=False,
        default=False
    )
    task_complete_before: _orm.Mapped[_dt] = _orm.mapped_column(
        _sql.DateTime
    )
    task_fail_on_late_complete: _orm.Mapped[bool] = _orm.mapped_column(
        _sql.Boolean,
        nullable=False,
        default=False
    )

    # relationships

    default_actor: _orm.Mapped[
        "DefaultActor"] = _orm.relationship(back_populates="task_delegations")

    incoming_task_type: _orm.Mapped[
        "TaskType"] = _orm.relationship(back_populates="incoming_in_task_delegations")

    outcoming_task_type: _orm.Mapped[
        "TaskType"] = _orm.relationship(back_populates="outcoming_in_task_delegations")

    # composite primary key
    __table_args__ = (
        _schema.PrimaryKeyConstraint(default_actor_id, incoming_task_type_id, outcoming_task_type_id),
        {},
    )

    def get_attachments(self, attachments_type: _T) -> _t.Generator[_T, None, None]:
        # I'm not found any other ways to save type hinting
        if attachments_type is not self.attachment_type:
            raise TypeError("wrong attachments type")

        # todo: find ways to replace
        attachments = eval(
            f"filter((lambda a: {self.filter_}), {self.source})",
            {},
            {"self": self},
        )
        _check_type(attachments, _t.Generator[_T, None, None])
        return attachments

    @_orm.validates("source")
    def _validate_source(self, _, source_: str):
        if not source_.startswith("self."):
            raise ValueError("Illegal source")

    @_orm.validates("attachments_type_name")
    def _validate_attachments_type_name(self, _, name: str):
        if name not in globals():
            raise ValueError("Illegal attachments type name")


class DefaultActor(_Base):
    __tablename__ = "DefaultActor"

    """
    Virtual actors
    """

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    actor_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Actor.id"),
        index=True,
        unique=True,
        nullable=False,
    )
    name: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        unique=True,
        index=True
    )

    # relationships

    actor: _orm.Mapped[
        "Actor"] = _orm.relationship(back_populates="default_actor")

    task_delegations: _orm.Mapped[
        _t.List["DefaultActorTaskDelegation"]] = _orm.relationship(back_populates="default_actor")

    restaurant: _orm.Mapped[
        _t.Optional["Restaurant"]] = _orm.relationship(back_populates="default_actor")

    restaurant_external_department: _orm.Mapped[
        _t.Optional["RestaurantExternalDepartment"]] = _orm.relationship(back_populates="default_actor")

    restaurant_internal_department: _orm.Mapped[
        _t.Optional["RestaurantInternalDepartment"]] = _orm.relationship(back_populates="default_actor")


class TaskType(_Base):
    __tablename__ = "TaskType"

    """
    Task templates
    """

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    name: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        unique=True,
        index=True
    )

    # relationships

    groups: _orm.Mapped[
        _t.List["TaskTypeGroupType"]] = _orm.relationship(back_populates="type")

    incoming_in_task_delegations: _orm.Mapped[
        _t.List["DefaultActorTaskDelegation"]] = _orm.relationship(back_populates="incoming_task_type")

    outcoming_in_task_delegations: _orm.Mapped[
        _t.List["DefaultActorTaskDelegation"]] = _orm.relationship(back_populates="outcoming_task_type")


class TaskTypeGroup(_Base):
    __tablename__ = "TaskTypeGroup"

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    name: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        unique=True,
        index=True,
        nullable=False
    )

    # relationships

    types: _orm.Mapped[
        _t.List["TaskTypeGroupType"]] = _orm.relationship(back_populates="group")

    restaurant_employee_position_access_levels: _orm.Mapped[
        _t.List["RestaurantEmployeePositionAccessLevel"]] = _orm.relationship(back_populates="task_type_group")

    personal_access_levels: _orm.Mapped[
        _t.List["ActorAccessLevel"]] = _orm.relationship(back_populates="task_type_group")


class TaskTypeGroupType(_Base):
    __tablename__ = "TaskTypeGroupType"

    # columns
    group_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("TaskTypeGroup.id"),
        primary_key=True
    )
    type_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("TaskType.id"),
        primary_key=True
    )

    # relationships

    group: _orm.Mapped[
        "TaskTypeGroup"] = _orm.relationship(back_populates="types")

    type: _orm.Mapped[
        "TaskType"] = _orm.relationship(back_populates="groups")

    # composite primary key
    __table_args__ = (_schema.PrimaryKeyConstraint(group_id, type_id), {})


class ActorAccessLevel(_Base):
    __tablename__ = "ActorAccessLevel"

    """
    Personal access level issued by another actor
    """

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True
    )
    actor_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Actor.id"),
        nullable=False,
        index=True
    )
    task_type_group_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("TaskTypeGroup.id"),
        nullable=False,
        index=True,
    )
    task_target_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("TaskTarget.id"),
        index=True,
        unique=True
    )
    role: _orm.Mapped[_types.enums.AccessRole] = _orm.mapped_column(
        _sql.Enum(_types.enums.AccessRole),
        nullable=False,
        index=True
    )

    # relationships

    actor: _orm.Mapped[
        "Actor"] = _orm.relationship(back_populates="personal_access_levels")

    task_type_group: _orm.Mapped[
        "TaskTypeGroup"] = _orm.relationship(back_populates="personal_access_levels")

    task_target: _orm.Mapped[
        "TaskTarget"] = _orm.relationship(back_populates="defining_access_level")


class TaskTarget(_Base):
    __tablename__ = "TaskTarget"

    """
    Action for which the task was created
    """

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )

    # relationships

    task: _orm.Mapped[
        "Task"] = _orm.relationship(back_populates="target")

    types: _orm.Mapped[
        _t.List["TaskTargetTypeTarget"]] = _orm.relationship(back_populates="target")

    supply: _orm.Mapped[
        _t.Optional["Supply"]] = _orm.relationship(back_populates="task_target")

    salary: _orm.Mapped[
        _t.Optional["Salary"]] = _orm.relationship(back_populates="task_target")

    writeoff: _orm.Mapped[
        _t.Optional["WriteOff"]] = _orm.relationship(back_populates="task_target")

    customer_order: _orm.Mapped[
        _t.Optional["CustomerOrder"]] = _orm.relationship(back_populates="task_target")

    customer_payment: _orm.Mapped[
        _t.Optional["CustomerPayment"]] = _orm.relationship(back_populates="task_target")

    supply_order: _orm.Mapped[
        _t.Optional["SupplyOrder"]] = _orm.relationship(back_populates="task_target")

    supply_payment: _orm.Mapped[
        _t.Optional["SupplyPayment"]] = _orm.relationship(back_populates="task_target")

    defining_access_level: _orm.Mapped[
        _t.Optional["ActorAccessLevel"]] = _orm.relationship(back_populates="task_target")

    discount_group: _orm.Mapped[
        _t.Optional["DiscountGroup"]] = _orm.relationship(back_populates="task_target")

    dicsount: _orm.Mapped[
        _t.Optional["Discount"]] = _orm.relationship(back_populates="task_target")


class TaskTargetType(_Base):
    __tablename__ = "TaskTargetType"

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    name: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        nullable=False,
        unique=True,
        index=True
    )

    # relationships

    targets: _orm.Mapped[
        _t.List["TaskTargetTypeTarget"]] = _orm.relationship(back_populates="type")


class TaskTargetTypeTarget(_Base):
    __tablename__ = "TaskTargetTypeTarget"

    # columns
    type_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("TaskTargetType.id"),
        primary_key=True
    )
    target_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("TaskTarget.id"),
        primary_key=True
    )

    type: _orm.Mapped[
        "TaskTargetType"] = _orm.relationship(back_populates="targets")

    target: _orm.Mapped[
        "TaskTarget"] = _orm.relationship(back_populates="types")

    # composite primary key
    __table_args__ = (_schema.PrimaryKeyConstraint(type_id, target_id), {})


class SubTask(_Base):
    __tablename__ = "SubTask"

    """
    A subtask created by the executor of the main task to complete it
    """

    # columns
    child_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Task.id"),
        primary_key=True
    )
    parent_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Task.id"),
        primary_key=True
    )
    priority: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        nullable=False,
        default=0
    )

    # relationships

    subtasks: _orm.Mapped[
        _t.List["Task"]] = _orm.relationship(back_populates="parent")

    parent: _orm.Mapped[
        "Task"] = _orm.relationship(back_populates="subtasks")

    # composite primary key
    __table_args__ = (_schema.PrimaryKeyConstraint(child_id, parent_id), {})


class User(_Base):
    __tablename__ = "User"

    """
    People (real actor)
    """

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    hashed_password: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        nullable=False
    )
    actor_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Actor.id"),
        nullable=False,
        index=True
    )
    role: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        nullable=False,
        index=True
    )
    email: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        unique=True,
        index=True,
        nullable=False
    )
    phone: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        unique=True,
        index=True,
        nullable=True
    )
    telegram: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        unique=True,
        index=True,
        nullable=True
    )
    lname: _orm.Mapped[_t.Optional[str]] = _orm.mapped_column(
        _sql.String,
        nullable=True
    )
    fname: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        nullable=False
    )
    sname: _orm.Mapped[_t.Optional[str]] = _orm.mapped_column(
        _sql.String,
        nullable=True
    )
    gender: _orm.Mapped[_t.Optional[bool]] = _orm.mapped_column(
        _sql.Boolean,
        nullable=True
    )
    address: _orm.Mapped[_t.Optional[str]] = _orm.mapped_column(
        _sql.String,
        nullable=True
    )
    last_online: _orm.Mapped[_dt] = _orm.mapped_column(
        _sql.DateTime,
        nullable=False,
        default=_dt.utcnow,
        index=True
    )
    created: _orm.Mapped[_dt] = _orm.mapped_column(
        _sql.DateTime,
        nullable=False,
        index=True
    )
    deleted: _orm.Mapped[_t.Optional[_dt]] = _orm.mapped_column(
        _sql.DateTime,
        nullable=True
    )

    # relationships

    actor: _orm.Mapped[
        "Actor"] = _orm.relationship(back_populates="user")

    restaurant_employee: _orm.Mapped[
        _t.Optional["RestaurantEmployee"]] = _orm.relationship(back_populates="user")

    customer: _orm.Mapped[
        _t.Optional["Customer"]] = _orm.relationship(back_populates="user")

    verifications: _orm.Mapped[
        _t.List["Verification"]] = _orm.relationship(back_populates="user")

    def verify_password(self, password: str) -> bool:
        return _hash.bcrypt.verify(password, self.hashed_password)

    @_orm.validates("email")
    def _validate_email(self, _, email: str):
        try:
            _validate_email(email, check_deliverability=False)
        except _EmailError:
            raise _types.exceptions.EmailValidationError

    @_orm.validates("phone")
    def _validate_phone(self, _, phone: str):
        if not _re.match(_cfg.PHONE_VALIDATION_REGEX, phone):
            raise _types.exceptions.PhoneValidationError

    # todo: check tg user_id existence

    @property
    def verificated_fields(self) -> _t.Set[_types.enums.VerificationFieldName]:
        names = set(e for e in _types.enums.VerificationFieldName)
        return names - set(v.field_name for v in self.verifications)


class Verification(_Base):
    __tablename__ = "Verification"

    """
    User contact data awaiting confirmaion
    """

    # columns
    user_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("User.id"),
        primary_key=True
    )
    field_name: _orm.Mapped[_types.enums.VerificationFieldName] = _orm.mapped_column(
        _sql.Enum(_types.enums.VerificationFieldName),
        primary_key=True
    )
    value: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        nullable=False,
        unique=True
    )

    # relationships

    user: _orm.Mapped[
        "User"] = _orm.relationship(back_populates="verifications")

    # composite primary key
    __table_args__ = (_schema.PrimaryKeyConstraint(user_id, field_name), {})


class RestaurantEmployeePosition(_Base):
    __tablename__ = "RestaurantEmployeePosition"

    """
    Job title
    """

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    name: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        unique=True,
        nullable=False,
        index=True
    )
    salary: _orm.Mapped[float] = _orm.mapped_column(
        _sql.Float,
        nullable=False
    )
    expierence_coefficient: _orm.Mapped[float] = _orm.mapped_column(
        _sql.Float,
        nullable=False,
        default=1
    )

    # relationships

    employees: _orm.Mapped[
        _t.List["RestaurantEmployee"]] = _orm.relationship(back_populates="position")

    access_levels: _orm.Mapped[
        _t.List["RestaurantEmployeePositionAccessLevel"]] = _orm.relationship(back_populates="position")

    @_orm.validates("expierence_coefficient")
    def _validate_expierence_coefficient(self, k: str, v: float):
        _check_value(v, k, 1, "ge")
        _check_value(v, k, _cfg.MAX_EXPIERENCE_COEFFICIENT, "le")

    @_orm.validates("salary")
    def _validate_salary(self, k: str, v: float):
        _check_value(v, k, 0, "gt")


class RestaurantEmployeePositionAccessLevel(_Base):
    __tablename__ = "RestaurantEmployeePositionAccessLevel"

    """
    Group access levels for all restaurant employees in a specified position
    """

    # columns
    position_id = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("RestaurantEmployeePosition.id"),
        primary_key=True,
    )
    task_type_group_id = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("TaskTypeGroup.id"),
        primary_key=True
    )
    role: _orm.Mapped[_types.enums.AccessRole] = _orm.mapped_column(
        _sql.Enum(_types.enums.AccessRole),
        nullable=False,
        index=True
    )

    # relationships

    position: _orm.Mapped[
        "RestaurantEmployeePosition"] = _orm.relationship(back_populates="access_levels")

    task_type_group: _orm.Mapped[
        "TaskTypeGroup"] = _orm.relationship(back_populates="restaurant_employee_position_access_levels")

    # composite primary key
    __table_args__ = (
        _schema.PrimaryKeyConstraint(position_id, task_type_group_id),
        {},
    )


class RestaurantEmployee(_Base):
    __tablename__ = "RestaurantEmployee"

    """
    Base model for each restaurant employee
    """

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    user_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("User.id"),
        nullable=False,
        unique=True
    )
    hiring_date: _orm.Mapped[_date] = _orm.mapped_column(
        _sql.Date,
        nullable=False
    )
    fired_date: _orm.Mapped[_t.Optional[_date]] = _orm.mapped_column(
        _sql.Date,
        nullable=True
    )
    on_shift: _orm.Mapped[bool] = _orm.mapped_column(
        _sql.Boolean,
        nullable=False,
        index=True
    )
    position_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("RestaurantEmployeePosition.id"),
        nullable=False,
        index=True,
    )
    restaurant_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Restaurant.id"),
        index=True,
        nullable=False,
    )

    # relationships

    user: _orm.Mapped[
        "User"] = _orm.relationship(back_populates="restaurant_employee")

    position: _orm.Mapped[
        "RestaurantEmployeePosition"] = _orm.relationship(back_populates="employees")

    salaries: _orm.Mapped[
        _t.List["Salary"]] = _orm.relationship(back_populates="restaurant_employee")

    restaurant: _orm.Mapped[
        "Restaurant"] = _orm.relationship(back_populates="employees")


class Customer(_Base):
    __tablename__ = "Customer"

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    user_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("User.id"),
        nullable=False,
        unique=True,
        index=True,
    )
    bonus_points: _orm.Mapped[float] = _orm.mapped_column(
        _sql.Float,
        nullable=False,
        default=0
    )

    # relationships

    user: _orm.Mapped[
        "User"] = _orm.relationship(back_populates="customer")

    favorites: _orm.Mapped[
        _t.List["CustomerFavoriteProduct"]] = _orm.relationship(back_populates="customer")

    shopping_cart_products: _orm.Mapped[
        _t.List["CustomerFavoriteProduct"]] = _orm.relationship(back_populates="customer")

    @_orm.validates("bonuts_points")
    def _validate_bonus_points(self, k: str, v: float):
        _check_value(v, k, 0, "ge")


class Material(_Base, _types.abstracts.ItemImplementation):
    __tablename__ = "Material"

    """
    Supplied consumables
    """

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    item_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Item.id"),
        unique=True,
        nullable=False,
        index=True,
    )
    name: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        unique=True,
        nullable=False,
        index=True
    )
    unit: _orm.Mapped[_types.enums.ItemUnit] = _orm.mapped_column(
        _sql.Enum(_types.enums.ItemUnit),
        nullable=False
    )
    price: _orm.Mapped[float] = _orm.mapped_column(
        _sql.Float,
        nullable=False
    )
    best_before: _orm.Mapped[_t.Optional[_dt]] = _orm.mapped_column(
        _sql.DateTime,
        nullable=False
    )
    group_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("MaterialGroup.id"),
        nullable=False
    )
    created: _orm.Mapped[_dt] = _orm.mapped_column(
        _sql.DateTime,
        nullable=False,
        index=True
    )

    # relationships
    item: _orm.Mapped[
        "Item"] = _orm.relationship(back_populates="material")

    group: _orm.Mapped[
        "MaterialGroup"] = _orm.relationship(back_populates="materials")

    ingridients: _orm.Mapped[
        _t.List["IngridientMaterial"]] = _orm.relationship(back_populates="material")

    allergic_flags: _orm.Mapped[
        _t.List["MaterialAllergicFlag"]] = _orm.relationship(back_populates="material")

    stock_balance: _orm.Mapped[
        _t.List["MaterialStockBalance"]] = _orm.relationship(back_populates="material")

    @_orm.validates("price")
    def _validate_price(self, k: str, v: float):
        _check_value(v, k, 0, "gt")


class MaterialStockBalance(_Base):
    __tablename__ = "MaterialStockBalance"

    # columns
    material_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Material.id"),
        primary_key=True
    )
    restaurant_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Restaurant.id"),
        primary_key=True
    )
    balance: _orm.Mapped[_t.Optional[float]] = _orm.mapped_column(
        _sql.Float,
        nullable=True
    )

    # relationships
    material: _orm.Mapped[
        "Material"] = _orm.relationship(back_populates="stock_balance")

    restaurant: _orm.Mapped[
        "Restaurant"] = _orm.relationship(back_populates="stock_balance")

    # composite primary key
    __table_args__ = (
        _schema.PrimaryKeyConstraint(material_id, restaurant_id),
        {},
    )


class MaterialGroup(_Base):
    __tablename__ = "MaterialGroup"

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    name: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        nullable=False,
        unique=True,
        index=True
    )

    # relationships

    parent_group: _orm.Mapped[
        _t.Optional["MaterialSubGroup"]] = _orm.relationship(back_populates="child")

    subgroups: _orm.Mapped[
        _t.List["MaterialSubGroup"]] = _orm.relationship(back_populates="parent")


class MaterialSubGroup(_Base):
    __tablename__ = "MaterialSubGroup"

    # columns
    parent_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("MaterialGroup.id"),
        primary_key=True
    )
    child_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("MaterialGroup.id"),
        primary_key=True
    )

    # relationships

    parent: _orm.Mapped[
        "MaterialGroup"] = _orm.relationship(back_populates="subgroups")

    child: _orm.Mapped[
        "MaterialGroup"] = _orm.relationship(back_populates="parent_group")

    # composite primary key
    __table_args__ = (_schema.PrimaryKeyConstraint(child_id, parent_id), {})


class Supply(_Base):
    __tablename__ = "Supply"

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    restaurant_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Restaurant.id"),
        nullable=False,
        index=True,
    )
    task_target_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("TaskTarget.id"),
        nullable=False,
        index=True,
    )

    # relationships

    task_target: _orm.Mapped[
        "TaskTarget"] = _orm.relationship(back_populates="supply")

    items: _orm.Mapped[
        _t.List["SupplyItem"]] = _orm.relationship(back_populates="supply")

    payment: _orm.Mapped[
        "SupplyPayment"] = _orm.relationship(back_populates="supply")


class SupplyItem(_Base):
    __tablename__ = "SupplyItem"

    # columns
    supply_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Supply.id"),
        primary_key=True
    )
    item_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Item.id"),
        primary_key=True
    )
    count: _orm.Mapped[float] = _orm.mapped_column(
        _sql.Float,
        nullable=False
    )
    price: _orm.Mapped[_t.Optional[float]] = _orm.mapped_column(
        _sql.Float,
        nullable=True
    )

    # relationships

    supply: _orm.Mapped[
        "Supply"] = _orm.relationship(back_populates="items")

    item: _orm.Mapped[
        "Item"] = _orm.relationship(back_populates="supplies")

    # composite primary key
    __table_args__ = (_schema.PrimaryKeyConstraint(supply_id, item_id), {})


class Ingridient(_Base):
    __tablename__ = "Ingridient"

    """
    Ingredient displayed in the dish composition
    """

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    name: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        unique=True,
        nullable=False,
        index=True
    )
    calories: _orm.Mapped[float] = _orm.mapped_column(
        _sql.Float,
        nullable=False
    )
    fats: _orm.Mapped[float] = _orm.mapped_column(
        _sql.Float,
        nullable=False
    )
    proteins: _orm.Mapped[float] = _orm.mapped_column(
        _sql.Float,
        nullable=False
    )
    carbohidrates: _orm.Mapped[float] = _orm.mapped_column(
        _sql.Float,
        nullable=False
    )
    created: _orm.Mapped[_dt] = _orm.mapped_column(
        _sql.DateTime,
        nullable=False
    )

    # relationships

    materials: _orm.Mapped[
        _t.List["IngridientMaterial"]] = _orm.relationship(back_populates="ingridient")

    products: _orm.Mapped[
        _t.List["ProductIngridient"]] = _orm.relationship(back_populates="ingridient")

    available_to_add_in_products: _orm.Mapped[
        _t.List["ProductAvailableExtraIngridient"]] = _orm.relationship(back_populates="ingridient")

    @property
    def nutritional_values(self) -> _types.schemas.NutritionalValues:
        return _types.schemas.NutritionalValues.model_validate(self)

    @property
    def allergic_flags(self) -> _t.Set[str]:
        # todo: check efficiency
        # may cause unnecessary calls to the database
        flags = set()
        for m in self.materials:
            for f in m.material.allergic_flags:
                flags.add(f.allergic_flag.name)
        return flags


class IngridientMaterial(_Base):
    __tablename__ = "IngridientMaterial"

    """
    Consumables that make up the ingredient
    """

    # columns
    material_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Material.id"),
        primary_key=True
    )
    ingridient_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Ingridient.id"),
        primary_key=True
    )
    im_ratio: _orm.Mapped[float] = _orm.mapped_column(
        _sql.Float,
        nullable=False
    )

    # relationships

    material: _orm.Mapped[
        "Material"] = _orm.relationship(back_populates="ingridients")

    ingridient: _orm.Mapped[
        "Ingridient"] = _orm.relationship(back_populates="materials")

    # composite primary key
    __table_args__ = (
        _schema.PrimaryKeyConstraint(ingridient_id, material_id),
        {},
    )


class Product(_Base):
    __tablename__ = "Product"

    """
    Item in the menu
    """

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    name: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        nullable=False,
        unique=True,
        index=True
    )
    price: _orm.Mapped[_t.Optional[float]] = _orm.mapped_column(
        _sql.Float,
        nullable=True
    )
    best_before: _orm.Mapped[_dt] = _orm.mapped_column(
        _sql.DateTime
    )
    status: _orm.Mapped[_types.enums.ProductStatus] = _orm.mapped_column(
        _sql.Enum(_types.enums.ProductStatus),
        nullable=False,
        index=True
    )
    own_production: _orm.Mapped[bool] = _orm.mapped_column(
        _sql.Boolean,
        nullable=False
    )
    avaible_in_online_order: _orm.Mapped[bool] = _orm.mapped_column(
        _sql.Boolean,
        nullable=False,
        index=True
    )
    tare_id: _orm.Mapped[_t.Optional[int]] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Tare.id"),
        nullable=True
    )

    # relationships

    ingridients: _orm.Mapped[
        _t.List["ProductIngridient"]] = _orm.relationship(back_populates="product")

    customers_who_added_to_favorites: _orm.Mapped[
        _t.List["CustomerFavoriteProduct"]] = _orm.relationship(back_populates="product")

    customers_who_added_to_shopping_cart: _orm.Mapped[
        _t.List["CustomerShoppingCartProduct"]] = _orm.relationship(back_populates="product")

    customer_orders: _orm.Mapped[
        _t.List["CustomerOrderProduct"]] = _orm.relationship(back_populates="product")

    available_extra_ingridients: _orm.Mapped[
        _t.List["ProductAvailableExtraIngridient"]] = _orm.relationship(back_populates="product")

    category: _orm.Mapped[
        "ProductCategoryProduct"] = _orm.relationship(back_populates="product")

    discounts: _orm.Mapped[
        _t.List["DiscountOptionProduct"]] = _orm.relationship(back_populates="product")

    tare: _orm.Mapped[
        _t.Optional["Tare"]] = _orm.relationship(back_populates="products")

    restaurants: _orm.Mapped[
        _t.List["RestaurantProduct"]] = _orm.relationship(back_populates="product")

    @_orm.validates("price")
    def _validate_price(self, k: _t.Literal["price"], v: float):
        _check_value(v, k, 0, "gt")

    @property
    def nutritianal_values(self) -> _types.schemas.NutritionalValues:
        values = _types.schemas.NutritionalValues(calories=0, fats=0, proteins=0, carbohydrates=0)
        for i in self.ingridients:
            values += i.ingridient.nutritional_values * i.ip_ratio
        return values

    @property
    def allergic_flags(self) -> _t.Set[str]:
        # todo: check efficiency
        # may cause unnecessary calls to the database
        flags = set()
        for i in self.ingridients:
            flags = flags.union(i.ingridient.allergic_flags)
        return flags


class RestaurantProduct(_Base):
    __tablename__ = "RestaurantProduct"

    """
    Product selling in a restaurant.

    To get suspend period, look for the Task with name
    'RestarauntProduct#<id> suspend'
    """

    # columns
    product_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Product.id"),
        primary_key=True
    )
    restaurant_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Restaurant.id"),
        primary_key=True
    )
    suspended: _orm.Mapped[bool] = _orm.mapped_column(
        _sql.Boolean,
        nullable=False,
        default=False,
        index=True
    )

    # relationships

    product: _orm.Mapped[
        "Product"] = _orm.relationship(back_populates="restaurants")

    restaurant: _orm.Mapped[
        "Restaurant"] = _orm.relationship(back_populates="products")

    __table_args__ = (
        _schema.PrimaryKeyConstraint(restaurant_id, product_id),
        {},
    )


class ProductIngridient(_Base):
    __tablename__ = "ProductIngridient"

    """
    Product composition with information on possible customization
    """

    # columns
    product_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Product.id"),
        primary_key=True
    )
    ingridient_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Ingridient.id"),
        primary_key=True
    )
    ip_ratio: _orm.Mapped[float] = _orm.mapped_column(
        _sql.Float,
        nullable=False
    )
    editable: _orm.Mapped[bool] = _orm.mapped_column(
        _sql.Boolean,
        nullable=False
    )
    edit_price: _orm.Mapped[_t.Optional[float]] = _orm.mapped_column(
        _sql.Float,
        nullable=True
    )
    max_change: _orm.Mapped[_t.Optional[float]] = _orm.mapped_column(
        _sql.Float,
        nullable=True
    )

    # relationships

    product: _orm.Mapped[
        "Product"] = _orm.relationship(back_populates="ingridients")

    ingridient: _orm.Mapped[
        "Ingridient"] = _orm.relationship(back_populates="products")

    # composite primary key
    __table_args__ = (
        _schema.PrimaryKeyConstraint(ingridient_id, product_id),
        {},
    )

    # validators
    @_orm.validates("edit_price", "max_change", "ip_ratio")
    def _validate_float_fields(self, k: str, v: float):
        _check_value(v, k, 0, "ge")


class CustomerFavoriteProduct(_Base):
    __tablename__ = "CustomerFavoriteProduct"

    """
    Product in user's favorites
    """

    # columns
    customer_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Customer.id"),
        primary_key=True
    )
    product_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Product.id"),
        primary_key=True
    )

    # relationships

    customer: _orm.Mapped[
        "Customer"] = _orm.relationship(back_populates="favorite_products")

    product: _orm.Mapped[
        "Product"] = _orm.relationship(back_populates="cusomers_who_added_to_favorites")

    # composite primary key
    __table_args__ = (
        _schema.PrimaryKeyConstraint(customer_id, product_id),
        {},
    )


class CustomerShoppingCartProduct(_Base):
    __tablename__ = "CustomerShoppingCartProduct"

    """
    Product in user shopping cart
    """

    # columns
    customer_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Customer.id"),
        primary_key=True
    )
    product_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Product.id"),
        primary_key=True
    )
    count: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        nullable=False,
        default=1
    )

    # relationships

    customer: _orm.Mapped[
        "Customer"] = _orm.relationship(back_populates="shopping_cart_products")

    product: _orm.Mapped[
        "Product"] = _orm.relationship(back_populates="customers_who_added_to_shopping_cart")

    # composite primary key
    __table_args__ = (
        _schema.PrimaryKeyConstraint(customer_id, product_id),
        {},
    )

    @_orm.validates("count")
    def _validate_count(self, k: _t.Literal["count"], v: int):
        _check_value(v, k, 1, "ge")


class CustomerOrder(_Base):
    __tablename__ = "CustomerOrder"

    """
    Order made via website or waiter's terminal
    """

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    task_target_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("TaskTarget.id"),
        nullable=False,
        unique=False,
        index=True,
    )
    restaurant_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Restaurant.id"),
        nullable=False,
        index=True,
    )
    status: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        nullable=False
    )

    # relationships

    task_target: _orm.Mapped[
        "TaskTarget"] = _orm.relationship(back_populates="customer_order")

    products: _orm.Mapped[
        _t.List["CustomerOrderProduct"]] = _orm.relationship(back_populates="customer_order")

    online_order: _orm.Mapped[
        _t.Optional["OnlineOrder"]] = _orm.relationship(back_populates="customer_order")

    waiter_order: _orm.Mapped[
        _t.Optional["WaiterOrder"]] = _orm.relationship(back_populates="customer_order")

    payment: _orm.Mapped[
        "CustomerPayment"] = _orm.relationship(back_populates="order")

    restaurant: _orm.Mapped[
        "Restaurant"] = _orm.relationship(back_populates="customer_orders")


class CustomerOrderProduct(_Base):
    __tablename__ = "CustomerOrderProduct"

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    order_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("CustomerOrder.id"),
        nullable=False,
        index=True,
    )
    product_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Product.id"),
        nullable=False,
        index=True
    )
    discount_option_id: _orm.Mapped[_t.Optional[int]] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("DiscountOption.id"),
        nullable=True
    )
    paid_by_bonus_points: _orm.Mapped[bool] = _orm.mapped_column(
        _sql.Boolean,
        nullable=False,
        default=False
    )
    count: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        nullable=False,
        default=1
    )

    # relationships

    customer_order: _orm.Mapped[
        "CustomerOrder"] = _orm.relationship(back_populates="products")

    product: _orm.Mapped[
        "Product"] = _orm.relationship(back_populates="customer_orders")

    discount_option: _orm.Mapped[
        _t.Optional["DiscountOption"]] = _orm.relationship(back_populates="order_products")

    changed_ingridients: _orm.Mapped[
        _t.List["CustomerOrderProductIngridientChange"]] = _orm.relationship(back_populates="product")

    @_orm.validates("count")
    def _validate_count(self, k: _t.Literal["count"], v: int):
        _check_value(v, k, 1, "ge")

    @property
    def allergic_flags(self) -> _t.Set[str]:
        """Set of all allergic flags excluding removed ingridients"""

        # todo: check efficiency
        # may cause unnecessary calls to the database
        flags = set()
        removed = tuple(i.ingridient.id for i in self.changed_ingridients)
        for i in self.product.ingridients:
            if i.ingridient.id in removed:
                continue
            flags = flags.union(i.ingridient.allergic_flags)
        return flags

    @property
    def nutritional_values(self) -> _types.schemas.NutritionalValues:
        """Total nutritional values after changing ingridients"""

        # todo: check efficiency
        # may cause unnecessary calls to the database

        values = self.product.nutritianal_values
        # NutritionalValue fields cannot be lower than 0
        values.calories += sum(i.ingridient.nutritional_values.calories for i in self.changed_ingridients)
        values.fats += sum(i.ingridient.nutritional_values.fats for i in self.changed_ingridients)
        values.proteins += sum(i.ingridient.nutritional_values.proteins for i in self.changed_ingridients)
        values.carbohydrates += sum(i.ingridient.nutritional_values.carbohydrates for i in self.changed_ingridients)
        return values


class OnlineOrder(_Base):
    __tablename__ = "OnlineOrder"

    """
    Purchase on the website
    """

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    order_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("CustomerOrder.id"),
        nullable=False,
        index=True,
        unique=True,
    )

    # relationships

    customer_order: _orm.Mapped[
        "CustomerOrder"] = _orm.relationship(back_populates="online_order")


class ProductAvailableExtraIngridient(_Base):
    __tablename__ = "ProductAvailableExtraIngridient"

    """
    Ingridients that can be added to a product
    """

    # columns
    product_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Product.id"),
        primary_key=True
    )
    ingridient_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Ingridient.id"),
        primary_key=True
    )
    price: _orm.Mapped[float] = _orm.mapped_column(
        _sql.Float,
        nullable=False
    )

    # relationships

    product: _orm.Mapped[
        "Product"] = _orm.relationship(back_populates="available_extra_ingridients")

    ingridient: _orm.Mapped[
        "Ingridient"] = _orm.relationship(back_populates="available_to_add_in_products")

    # composite primary key
    __table_args__ = (
        _schema.PrimaryKeyConstraint(ingridient_id, product_id),
        {},
    )

    @_orm.validates("price")
    def _validate_price(self, k: _t.Literal["price"], v: float):
        _check_value(v, k, 0, "ge")


class CustomerOrderProductIngridientChange(_Base):
    __tablename__ = "CustomerOrderProductIngridientChange"

    """
    Customized ingridients in order
    """

    # columns
    order_product_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("CustomerOrderProduct.id"),
        primary_key=True,
    )
    ingridient_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Ingridient.id"),
        primary_key=True
    )
    ip_ratio_change: _orm.Mapped[float] = _orm.mapped_column(
        _sql.Float,
        nullable=False
    )

    # relationships

    order_product: _orm.Mapped[
        "CustomerOrderProduct"] = _orm.relationship(back_populates="changed_ingridients")

    ingridient: _orm.Mapped[
        "Ingridient"] = _orm.relationship(back_populates="changed_in_order_products")

    # composite primary key
    __table_args__ = (
        _schema.PrimaryKeyConstraint(ingridient_id, order_product_id),
        {},
    )

    @_orm.validates("ip_ratio_change")
    def _validate_iprc(self, k: _t.Literal["ip_ratio_change"], v: float):
        _check_value(v, k, 0, "ge")


class CustomerOrderProductExtraIngridient(_Base):
    __tablename__ = "CustomerOrderExtraIngridient"

    """
    Extra ingridients in order
    """

    # columns
    order_product_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("CustomerOrderProduct.id"),
        primary_key=True,
    )
    ingridient_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Ingridient.id"),
        primary_key=True
    )
    count: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        nullable=False,
        default=1
    )

    # relationships

    order_product: _orm.Mapped[
        "CustomerOrderProduct"] = _orm.relationship(back_populates="extra_ingridients")

    ingridient: _orm.Mapped[
        "Ingridient"] = _orm.relationship(back_populates="added_to_order_products")

    # composite primary key
    __table_args__ = (
        _schema.PrimaryKeyConstraint(ingridient_id, order_product_id),
        {},
    )

    @_orm.validates("count")
    def _validate_count(self, k: _t.Literal["count"], v: int):
        _check_value(v, k, 1, "ge")


class Table(_Base):
    __tablename__ = "Table"

    """
    Table in a restaurant
    """

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    number: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        nullable=False,
        index=True
    )
    location_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("TableLocation.id"),
        nullable=False,
        index=True,
    )

    # relationships

    location: _orm.Mapped[
        "TableLocation"] = _orm.relationship(back_populates="tables")

    waiter_orders: _orm.Mapped[
        _t.List["WaiterOrder"]] = _orm.relationship(back_populates="table")


class TableLocation(_Base):
    __tablename__ = "TableLocation"

    """
    Location with tables (floor, roof, etc.)
    """

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    name: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        unique=True,
        index=True,
        nullable=False
    )
    restaurant_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Restaurant.id"),
        nullable=False,
        index=True,
    )

    # relationships

    tables: _orm.Mapped[
        _t.List["Table"]] = _orm.relationship(back_populates="location")

    restaurant: _orm.Mapped[
        "Restaurant"] = _orm.relationship(back_populates="table_locations")


class WaiterOrder(_Base):
    __tablename__ = "WaiterOrder"

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    table_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Table.id"),
        nullable=False
    )
    order_Id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("CustomerOrder.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    # relationships

    table: _orm.Mapped[
        "Table"] = _orm.relationship(back_populates="waiter_orders")

    customer_order: _orm.Mapped[
        "CustomerOrder"] = _orm.relationship(back_populates="waiter_order")


class Salary(_Base):
    __tablename__ = "Salary"

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    task_target_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("TaskTarget.id"),
        nullable=False,
        unique=True,
        index=True,
    )
    restaurant_employee_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("RestaurantEmployee.id"),
        nullable=False,
        index=True,
    )
    bonus: _orm.Mapped[_t.Optional[float]] = _orm.mapped_column(
        _sql.Float,
        nullable=True
    )

    # relationships

    task_target: _orm.Mapped[
        "TaskTarget"] = _orm.relationship(back_populates="salary")

    restaurant_employee: _orm.Mapped[
        "RestaurantEmployee"] = _orm.relationship(back_populates="salaries")


class AllergicFlag(_Base):
    __tablename__ = "AllergicFlag"

    """
    Possible options for risk groups and allergies
    """

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    name: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        unique=True,
        index=True,
        nullable=False
    )

    # relationships

    materials: _orm.Mapped[
        _t.List["MaterialAllergicFlag"]] = _orm.relationship(back_populates="allergic_flag")


class MaterialAllergicFlag(_Base):
    __tablename__ = "MaterialAllergicFlag"

    """
    Allergic flags of the consumable
    """

    # columns
    material_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Material.id"),
        primary_key=True
    )
    flag_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("AllergicFlag.id"),
        primary_key=True
    )

    # relationships

    material: _orm.Mapped[
        "Material"] = _orm.relationship(back_populates="allergic_flags")

    allergic_flag: _orm.Mapped[
        "AllergicFlag"] = _orm.relationship(back_populates="materials")

    # composite primary key
    __table_args__ = (_schema.PrimaryKeyConstraint(material_id, flag_id), {})


class ProductCategory(_Base):
    __tablename__ = "ProductCategory"

    """
    Menu section
    """

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    name: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        unique=True,
        index=True,
        nullable=False
    )

    # relationships

    products: _orm.Mapped[
        _t.List["ProductCategoryProduct"]] = _orm.relationship(back_populates="product_category")


class ProductCategoryProduct(_Base):
    __tablename__ = "ProductCategoryProduct"

    # columns
    product_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Product.id"),
        primary_key=True
    )
    category_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("ProductCategory.id"),
        primary_key=True
    )

    # relationships

    product: _orm.Mapped[
        "Product"] = _orm.relationship(back_populates="category")

    product_category: _orm.Mapped[
        "ProductCategory"] = _orm.relationship(back_populates="products")

    # composite primary key
    __table_args__ = (
        _schema.PrimaryKeyConstraint(product_id, category_id),
        {},
    )


class CustomerPayment(_Base):
    __tablename__ = "CustomerPayment"

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    order_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("CustomerOrder.id"),
        unique=True,
        nullable=False,
        index=True,
    )
    task_target_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("TaskTarget.id"),
        nullable=False,
        index=True,
        unique=True,
    )

    # relationships

    order: _orm.Mapped[
        "CustomerOrder"] = _orm.relationship(back_populates="payment")

    task_target: _orm.Mapped[
        "TaskTarget"] = _orm.relationship(back_populates="customer_payment")


class DiscountGroup(_Base):
    __tablename__ = "DiscountGroup"

    """
    Named menu section with promotional items
    """

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    name: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        nullable=False
    )
    task_target_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("TaskTarget.id"),
        index=True,
        unique=True,
        nullable=False,
    )

    # relationships

    task_target: _orm.Mapped[
        "TaskTarget"] = _orm.relationship(back_populates="discount_group")

    discounts: _orm.Mapped[
        _t.List["Discount"]] = _orm.relationship(back_populates="group")


class Discount(_Base):
    __tablename__ = "Discount"

    """
    Single promotional offer
    """

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    type: _orm.Mapped[_types.enums.DiscountType] = _orm.mapped_column(
        _sql.Enum(_types.enums.DiscountType),
        nullable=False,
        index=True
    )
    promocode: _orm.Mapped[_t.Optional[str]] = _orm.mapped_column(
        _sql.String,
        nullable=True,
        index=True,
        unique=True
    )
    group_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("DiscountGroup.id"),
        nullable=False,
        index=True,
    )
    delivery_only: _orm.Mapped[bool] = _orm.mapped_column(
        _sql.Boolean,
        nullable=False,
        index=True,
        default=False
    )
    name: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        index=True,
        nullable=False
    )
    description: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        default="",
        nullable=False
    )
    condition: _orm.Mapped[_t.Optional[str]] = _orm.mapped_column(
        _sql.String,
        nullable=True
    )
    value: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        nullable=False
    )
    task_target_id = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("TaskTarget.id"),
        nullable=False,
        unique=True,
    )

    # relationships

    task_target: _orm.Mapped[
        "TaskTarget"] = _orm.relationship(back_populates="discount")

    group: _orm.Mapped[
        "DiscountGroup"] = _orm.relationship(back_populates="discounts")

    options: _orm.Mapped[
        _t.List["DiscountOption"]] = _orm.relationship(back_populates="discount")

    restaurants: _orm.Mapped[
        _t.List["RestaurantDiscount"]] = _orm.relationship(back_populates="discount")


class RestaurantDiscount(_Base):
    __tablename__ = "RestaurantDiscount"

    """
    Discounts offered in a restaurant
    """

    # columns
    restaurant_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Restaurant.id"),
        primary_key=True
    )
    discount_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Discount.id"),
        primary_key=True
    )

    # relationships

    restaurant: _orm.Mapped[
        "Restaurant"] = _orm.relationship(back_populates="discounts")

    discount: _orm.Mapped[
        "Discount"] = _orm.relationship(back_populates="restaurants")

    # composite primary key
    __table_args__ = (
        _schema.PrimaryKeyConstraint(restaurant_id, discount_id),
        {},
    )


class CustomerOrderDiscount(_Base):
    __tablename__ = "CustomerOrderDiscount"

    """
    Discounts used in order
    """

    # columns
    customer_order_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("CustomerOrder.id"),
        primary_key=True
    )
    discount_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Discount.id"),
        primary_key=True
    )

    # relationshis

    customer_order: _orm.Mapped[
        "CustomerOrder"] = _orm.relationship(back_populates="discounts")

    discount: _orm.Mapped[
        "Discount"] = _orm.relationship(back_populates="orders")


class DiscountOption(_Base):
    __tablename__ = "DiscountOption"

    """
    A set of products from which you can choose one to participate
    in the promotion.
    """

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    title: _orm.Mapped[_t.Optional[str]] = _orm.mapped_column(
        _sql.String,
        nullable=True
    )
    discount_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Discount.id"),
        nullable=False
    )

    # relationships

    discount: _orm.Mapped[
        "Discount"] = _orm.relationship(back_populates="options")

    products: _orm.Mapped[
        "DiscountOptionProduct"] = _orm.relationship(back_populates="option")


class DiscountOptionProduct(_Base):
    __tablename__ = "DiscountOptionProduct"

    """
    Product that can be selected from the list as option to participate
    in the promotion
    """

    # columns
    discount_option_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("DiscountOption.id"),
        primary_key=True
    )
    product_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Product.id"),
        primary_key=True
    )

    # relationships

    option: _orm.Mapped[
        "DiscountOption"] = _orm.relationship(back_populates="products")

    product: _orm.Mapped[
        "Product"] = _orm.relationship(back_populates="discounts")


class SupplyOrder(_Base, _types.abstracts.ItemImplementationCollection):
    __tablename__ = "SupplyOrder"

    """
    Order for the supply
    """

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    task_target_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("TaskTarget.id"),
        index=True,
        nullable=False,
        unique=True,
    )

    # relationships

    task_target: _orm.Mapped[
        "TaskTarget"] = _orm.relationship(back_populates="supply_order")

    items: _orm.Mapped[
        _t.List["SupplyOrderItem"]] = _orm.relationship(back_populates="kitchen_order")


class SupplyOrderItem(_Base, _types.abstracts.ItemImplementationRelation):
    __tablename__ = "SupplyOrderItem"

    # columns
    supply_order_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("SupplyOrder.id"),
        primary_key=True
    )
    item_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Item.id"),
        primary_key=True
    )
    count: _orm.Mapped[float] = _orm.mapped_column(
        _sql.Float,
        nullable=False
    )

    # relationships

    supply_order: _orm.Mapped[
        "SupplyOrder"] = _orm.relationship(back_populates="items")

    item: _orm.Mapped[
        "Item"] = _orm.relationship(back_populates="supply_orders")

    # composite primary key
    __table_args__ = (
        _schema.PrimaryKeyConstraint(supply_order_id, item_id),
        {},
    )

    @_orm.validates("count")
    def _validate_count(self, k: _t.Literal["count"], v):
        _check_value(v, k, 1, "ge")

    @property
    def _collection(self):  # ovverides abstract property
        return self.supply_order


class WriteOffReason(_Base):
    __tablename__ = "WriteOffReason"

    """
    Write-off act (the reason why consumables can be written off)
    """

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    name: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        unique=True,
        nullable=False,
        index=True
    )
    descritption: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String
    )
    group_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("WriteOffReasonGroup.id"),
        nullable=False
    )

    # relationships

    group: _orm.Mapped[
        "WriteOffReasonGroup"] = _orm.relationship(back_populates="reasons")

    writeoffs: _orm.Mapped[
        _t.List["WriteOff"]] = _orm.relationship(back_populates="reason")


class WriteOffReasonGroup(_Base):
    __tablename__ = "WriteOffReasonGroup"

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    name: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        unique=True,
        nullable=False,
        index=True
    )
    description: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        nullable=False,
        default=""
    )

    # relationships

    reasons: _orm.Mapped[
        _t.List["WriteOffReason"]] = _orm.relationship(back_populates="group")


class WriteOff(_Base, _types.abstracts.ItemImplementationCollection):
    __tablename__ = "WriteOff"

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    task_target_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("TaskTarget.id"),
        nullable=False,
        index=True,
        unique=True,
    )
    reason_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("WriteOffReason.id"),
        nullable=False,
        index=True,
    )

    # relationships

    task_target: _orm.Mapped[
        "TaskTarget"] = _orm.relationship(back_populates="writeoff")

    reason: _orm.Mapped[
        "WriteOffReason"] = _orm.relationship(back_populates="writeoffs")

    items: _orm.Mapped[
        _t.List["WriteOffItem"]] = _orm.relationship(back_populates="writeoff")


class WriteOffItem(_Base, _types.abstracts.ItemImplementationRelation):
    __tablename__ = "WriteOffItem"

    # columns
    writeoff_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("WriteOff.id"),
        primary_key=True
    )
    item_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Item.id"),
        primary_key=True
    )
    count: _orm.Mapped[float] = _orm.mapped_column(
        _sql.Float,
        nullable=False
    )

    # relationshils

    writeoff: _orm.Mapped[
        "WriteOff"] = _orm.relationship(back_populates="materials")

    item: _orm.Mapped[
        "Item"] = _orm.relationship(back_populates="writeoffs")

    # composite primary key
    __table_args__ = (_schema.PrimaryKeyConstraint(writeoff_id, item_id), {})

    @property
    def _collection(self):  # overrides abstract property
        return self.writeoff


class SupplyPayment(_Base):
    __tablename__ = "SupplyPayment"

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    task_target_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("TaskTarget.id"),
        index=True,
        unique=True,
        nullable=False,
    )
    supply_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Supply.id"),
        index=True,
        unique=True,
        nullable=False,
    )

    # relationships

    task_target: _orm.Mapped[
        "TaskTarget"] = _orm.relationship(back_populates="supply_payment")

    supply: _orm.Mapped[
        "Supply"] = _orm.relationship(back_populates="payment")


class Tare(_Base, _types.abstracts.ItemImplementation):
    __tablename__ = "Tare"

    """
    Packaging for delivered products
    """

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    item_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Item.id"),
        unique=True,
        nullable=False,
        index=True,
    )
    name: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        nullable=False
    )
    price: _orm.Mapped[_t.Optional[float]] = _orm.mapped_column(
        _sql.Float,
        nullable=True
    )
    group_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("TareGroup.id"),
        nullable=False,
        index=True,
    )

    # relationships

    item: _orm.Mapped[
        "Item"] = _orm.relationship(back_populates="tare")

    products: _orm.Mapped[
        _t.List["Product"]] = _orm.relationship(back_populates="tare")

    group: _orm.Mapped[
        "TareGroup"] = _orm.relationship(back_populates="tare")

    @_orm.validates("price")
    def _validate_price(self, k: _t.Literal["price"], v: float):
        _check_value(v, k, 0, "gt")


class TareGroup(_Base):
    __tablename__ = "TareGroup"

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    name: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        unique=True,
        nullable=False,
        index=True
    )

    # relationships

    tare: _orm.Mapped[
        _t.List["Tare"]] = _orm.relationship(back_populates="group")


class Inventory(_Base, _types.abstracts.ItemImplementation):
    __tablename__ = "Inventory"

    """
    Reestaraunt property
    """

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    item_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Item.id"),
        unique=True,
        nullable=False,
        index=True,
    )
    name: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        nullable=False,
        unique=True
    )
    group_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("InventoryGroup.id"),
        nullable=False
    )

    # relationships

    item: _orm.Mapped[
        "Item"] = _orm.relationship(back_populates="inventory")

    group: _orm.Mapped[
        "InventoryGroup"] = _orm.relationship(back_populates="inventory")


class InventoryGroup(_Base):
    __tablename__ = "InventoryGroup"

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    name: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        nullable=False,
        unique=True
    )

    # relationships

    inventory: _orm.Mapped[
        _t.List["Inventory"]] = _orm.relationship(back_populates="group")

    subgroups: _orm.Mapped[
        _t.List["InventorySubGroup"]] = _orm.relationship(back_populates="parent")

    parent_group: _orm.Mapped[
        _t.Optional["InventorySubGroup"]] = _orm.relationship(back_populates="child")


class InventorySubGroup(_Base):
    __tablename__ = "InventorySubGroup"

    # columns
    parent_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("InventoryGroup.id"),
        primary_key=True
    )
    child_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("InventoryGroup.id"),
        primary_key=True
    )

    # relationships

    parent: _orm.Mapped[
        "InventoryGroup"] = _orm.relationship(back_populates="subgroups")

    child: _orm.Mapped[
        "InventoryGroup"] = _orm.relationship(back_populates="parent_group")

    # composite primary key
    __table_args__ = (_schema.PrimaryKeyConstraint(parent_id, child_id), {})


class Item(_Base, _types.abstracts.Item):
    __tablename__ = "Item"

    """
    Any company property that is used to operate a restaurant and prepare food.
    """

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )

    # relationships
    material: _orm.Mapped[
        _t.Optional["Material"]] = _orm.relationship(back_populates="item")

    tare: _orm.Mapped[
        _t.Optional["Tare"]] = _orm.relationship(back_populates="item")

    inventory: _orm.Mapped[
        _t.Optional["Inventory"]] = _orm.relationship(back_populates="item")

    writeoffs: _orm.Mapped[
        _t.List["WriteOffItem"]] = _orm.relationship(back_populates="item")

    supply_orders: _orm.Mapped[
        _t.List["SupplyOrderItem"]] = _orm.relationship(back_populates="item")


class Task(_Base):
    __tablename__ = "Task"

    """
    The main object required to perform financially responsible tasks.

    Tasks cannot be created backdating.
    """

    # columns
    id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.Identity(),
        primary_key=True,
        index=True
    )
    name: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        nullable=False
    )
    comment: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String
    )
    status: _orm.Mapped[str] = _orm.mapped_column(
        _sql.String,
        nullable=False,
        index=True
    )
    target_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("TaskTarget.id"),
        nullable=False,
        index=True,
    )
    created: _orm.Mapped[_dt] = _orm.mapped_column(
        _sql.DateTime,
        nullable=False,
        default=_dt.utcnow,
        index=True
    )
    author_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Actor.id"),
        nullable=False,
        index=True
    )
    changed: _orm.Mapped[bool] = _orm.mapped_column(
        _sql.Boolean,
        nullable=False,
        default=False
    )
    start_execution: _orm.Mapped[_t.Optional[_dt]] = _orm.mapped_column(
        _sql.DateTime,
        index=True,
        nullable=True
    )
    execution_started: _orm.Mapped[_t.Optional[_dt]] = _orm.mapped_column(
        _sql.DateTime,
        index=True,
        nullable=True
    )
    fail_on_late_start: _orm.Mapped[bool] = _orm.mapped_column(
        _sql.Boolean,
        nullable=False,
        default=False
    )
    complete_before: _orm.Mapped[_t.Optional[_dt]] = _orm.mapped_column(
        _sql.DateTime,
        nullable=True
    )
    completed: _orm.Mapped[_t.Optional[_dt]] = _orm.mapped_column(
        _sql.DateTime,
        nullable=True
    )
    fail_on_late_complete: _orm.Mapped[bool] = _orm.mapped_column(
        _sql.Boolean,
        nullable=False,
        default=False
    )
    executor_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Actor.id"),
        nullable=False,
        index=True
    )
    approved: _orm.Mapped[_t.Optional[_dt]] = _orm.mapped_column(
        _sql.DateTime,
        index=True,
        nullable=True
    )
    inspector_id: _orm.Mapped[int] = _orm.mapped_column(
        _sql.Integer,
        _sql.ForeignKey("Actor.id"),
        nullable=False,
        index=True
    )

    # relationships

    task_type: _orm.Mapped[
        "TaskType"] = _orm.relationship(back_populates="tasks")

    target: _orm.Mapped[
        "TaskTarget"] = _orm.relationship(back_populates="task")

    author: _orm.Mapped[
        "Actor"] = _orm.relationship(back_populates="created_tasks")

    executor: _orm.Mapped[
        "Actor"] = _orm.relationship(back_populates="tasks_to_execute")

    inspector: _orm.Mapped[
        "Actor"] = _orm.relationship(back_populates="tasks_to_inspect")

    parent: _orm.Mapped[
        _t.Optional["SubTask"]] = _orm.relationship(back_populates="subtasks")

    subtasks: _orm.Mapped[
        _t.List["SubTask"]] = _orm.relationship(back_populates="parent")

    @_orm.validates("start_execution", "complete_before")
    def _validate_dates(self, k: str, v: _dt):
        _check_value(v, k, _dt.utcnow(), "ge")

    @property
    def is_started_late(self) -> bool:
        if not self.start_execution:
            return False
        elif not self.execution_started:
            return self.start_execution <= _dt.utcnow()
        else:
            return self.execution_started <= self.start_execution

    @property
    def is_completed_late(self) -> bool:
        if not self.complete_before:
            return False
        elif not self.completed:
            return self.complete_before <= _dt.utcnow()
        else:
            return self.complete_before < self.completed

    @property
    def subtasks_by_priority(self) -> _t.List[_t.Tuple["Task"]]:
        """
        Returns subtasks as list of bunches.

        Tasks in one bunch must be executed in parallel,
        and bunches must be executed sequentially
        """
        subs = sorted(self.subtasks, key=_operator.attrgetter("priority"))
        result = []
        level: _t.List[SubTask] = []
        for s in subs:
            if not level or level[-1].priority == s.priority:
                level.append(s)
            else:
                result.append(tuple(level))
                level = []
                level.append(s)
        return result
