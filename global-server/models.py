from datetime import datetime as _dt
from operator import attrgetter as _attr
from typing import Dict as _Dict
from typing import Generator as _Generator
from typing import List as _List
from typing import Optional as _Opt
from typing import Tuple as _Tuple
from typing import TypeVar as _TypeVar

import passlib.hash as _hash
import project_types as _types
from database import Base as _Base
from sqlalchemy import Boolean as _Bool
from sqlalchemy import Column as _Column
from sqlalchemy import DateTime as _Dt
from sqlalchemy import Enum as _Enum
from sqlalchemy import Float as _Float
from sqlalchemy import ForeignKey as _Fk
from sqlalchemy import Integer as _Int
from sqlalchemy import String as _Str
from sqlalchemy import Time as _Time
from sqlalchemy.orm import Mapped as _Map
from sqlalchemy.orm import reconstructor as _reconstructor
from sqlalchemy.orm import relationship as _rel
from sqlalchemy.orm import validates as _validates
from sqlalchemy.schema import PrimaryKeyConstraint as _PKConstraint
from typeguard import check_type as _check_type


T = _TypeVar("T")


class Actor(_Base):
    __tablename__ = "Actor"

    """
    Basic model for both real and virtual actors
    """

    # columns
    id = _Column(_Int, primary_key=True, index=True)

    # relationships
    created_tasks: _Map[_List["Task"]] = _rel(back_populates="author")
    tasks_to_execute: _Map[_List["Task"]] = _rel(back_populates="executor")
    tasks_to_inspect: _Map[_List["Task"]] = _rel(back_populates="inspector")
    default_actor: _Map[_Opt["DefaultActor"]] = _rel(back_populates="actor")
    user: _Map[_Opt["User"]] = _rel(back_populates="actor")
    personal_access_levels: _Map[_List["ActorAccessLevel"]] = _rel(
        back_populates="actor"
    )


class Restaurant(_Base):
    __tablename__ = "Restaurant"

    """
    Model describing a restaurant and it's local server
    """

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    default_actor_id = _Column(
        _Int, _Fk("DefaultActor.id"), nullable=False, unique=True, index=True
    )
    url = _Column(_Str, nullable=False, unique=True, index=True)
    address = _Column(_Str, nullable=False, unique=True, index=True)
    accepts_online_orders = _Column(_Bool, nullable=False, index=True)

    # relationships
    default_actor: _Map["DefaultActor"] = _rel(back_populates="restaurant")
    external_departments: _Map[_List["RestaurantExternalDepartment"]] = _rel(
        back_populates="restaurant"
    )
    internal_departments: _Map[_List["RestaurantInternalDepartment"]] = _rel(
        back_populates="restaraunt"
    )
    employees: _Map[_List["RestaurantEmployee"]] = _rel(
        back_populates="restaurant"
    )
    stock_balance: _Map[_List["MaterialStockBalance"]] = _rel(
        back_populates="restaurant"
    )
    products: _Map[_List["RestaurantProduct"]] = _rel(
        back_populates="restaurant"
    )
    customer_orders: _Map[_List["CustomerOrder"]] = _rel(
        back_populates="restaurant"
    )
    table_locations: _Map[_List["TableLocation"]] = _rel(
        back_populates="restaurant"
    )
    discounts: _Map[_List["RestaurantDiscount"]] = _rel(
        back_populates="restaurant"
    )


class RestaurantExternalDepartment(_Base):
    __tablename__ = "RestaurantExternalDepartment"

    """
    Restaurant department that issues orders
    (hall / pickup service / drive-thru / delivery)
    """

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    default_actor_id = _Column(
        _Int, _Fk("DefaultActor.id"), nullable=False, index=True
    )
    restaurant_id = _Column(
        _Int, _Fk("Restaurant.id"), index=True, nullable=False
    )
    type = _Column(_Str, nullable=False, index=True)

    # relationships
    restaurant: _Map["Restaurant"] = _rel(
        back_populates="external_departments"
    )
    working_hours: _Map[
        _List["RestaurantExternalDepartmentWorkingHours"]
    ] = _rel(back_populates="department")
    default_actor: _Map["DefaultActor"] = _rel(
        back_populates="restaurant_external_department"
    )

    # methods
    @property
    def working_hours_tuple(
        self,
    ) -> _Tuple[_types.schemas.WeekdayWorkingHours]:
        return tuple(  # pyright: ignore
            _types.schemas.WeekdayWorkingHours.model_validate(h)
            for h in sorted(self.working_hours, key=_attr("weekday"))
        )

    @property
    def working_hours_dict(
        self,
    ) -> _Dict[_types.enums.Weekday, _types.schemas.WeekdayWorkingHours]:
        return {
            k: v
            for k, v in (
                (_types.enums.Weekday(i), w)
                for i, w in enumerate(self.working_hours_tuple)
            )
        }


class RestaurantExternalDepartmentWorkingHours(_Base):
    __tablename__ = "RestaurantExternalDepartmentWorkingHours"

    """
    Restaurant external department working hours at a weekday
    """

    # columns
    department_id = _Column(
        _Int, _Fk("RestaurantExternalDepartment.id"), primary_key=True
    )
    weekday = _Column(_Enum(_types.enums.Weekday), primary_key=True)
    start = _Column(_Time, nullable=False, index=True)
    finish = _Column(_Time, nullable=False, index=True)

    # relationships
    department: _Map["RestaurantExternalDepartment"] = _rel(
        back_populates="working_hours"
    )


class RestaurantInternalDepartment(_Base):
    __tablename__ = "RestaurantInternalDepartment"

    """
    Restaurant department not involved in issuing orders
    """

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    name = _Column(_Str, nullable=False, index=True)
    default_actor_id = _Column(
        _Int, _Fk("DefaultActor.id"), nullable=False, index=True
    )
    restaurant_id = _Column(
        _Int, _Fk("Restaurant.id"), index=True, nullable=False
    )
    type = _Column(_Str, nullable=False, index=True)

    # relationships
    restaurant: _Map["Restaurant"] = _rel(
        back_populates="internal_departments"
    )
    default_actor: _Map["DefaultActor"] = _rel(
        back_populates="restaurant_internal_department"
    )
    sub_departments: _Map[_List["RestaurantInternalSubDepartment"]] = _rel(
        back_populates="parent"
    )
    parent_department: _Map["RestaurantInternalSubDepartment"] = _rel(
        back_populates="child"
    )


class RestaurantInternalSubDepartment(_Base):
    __tablename__ = "RestaurantInternalSubDepartment"

    """
    Internal restaraunt department that reports to a parent department
    """

    # columns
    parent_id = _Column(
        _Int, _Fk("RestaurantInternalDepartment.id"), primary_key=True
    )
    child_id = _Column(
        _Int, _Fk("RestaurantInternalDepartment.id"), primary_key=True
    )

    # relationships
    parent: _Map["RestaurantInternalDepartment"] = _rel(
        back_populates="sub_departments"
    )
    child: _Map["RestaurantInternalDepartment"] = _rel(
        back_populates="parent_department"
    )

    # composite primary key
    __table_args__ = (_PKConstraint(child_id, parent_id), {})


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

    @_reconstructor
    def _set_result_type(self):
        self.attachments_type = globals()[
            self.attachments_type_name
        ]  # pyright: ignore

    # columns
    default_actor_id = _Column(_Int, _Fk("DefaultActor.id"), primary_key=True)
    incoming_task_type_id = _Column(_Int, _Fk("TaskType.id"), primary_key=True)
    outcoming_task_type_id = _Column(
        _Int, _Fk("TaskType.id"), primary_key=True
    )

    # columns with python code that
    # must be used to collect delegation attachments
    source = _Column(_Str, nullable=False)
    filter_ = _Column(_Str, nullable=True)
    attachments_type_name = _Column(_Str, nullable=False)

    # columns for Task creation
    task_name = _Column(_Str, nullable=False)
    task_comment = _Column(_Str)
    task_start_execution = _Column(_Dt, index=True)
    task_fail_on_late_start = _Column(_Bool, nullable=False, default=False)
    task_complete_before = _Column(_Dt)
    task_fail_on_late_complete = _Column(_Bool, nullable=False, default=False)

    # relationships
    default_actor: _Map["DefaultActor"] = _rel(
        back_populates="task_delegations"
    )
    incoming_task_type: _Map["TaskType"] = _rel(
        back_populates="incoming_in_task_delegations"
    )
    outcoming_task_type: _Map["TaskType"] = _rel(
        back_populates="outcoming_in_task_delegations"
    )

    # composite primary key
    __table_args__ = (
        _PKConstraint(
            default_actor_id, incoming_task_type_id, outcoming_task_type_id
        ),
        {},
    )

    # methods
    def get_attachments(
        self, attachments_type: T  # pyright: ignore
    ) -> _Generator[T, None, None]:
        # I'm not found any other ways to save type hinting
        if attachments_type is not self.attachment_type:
            raise TypeError("wrong attachment type")

        # todo: find ways to replace
        attachments = eval(
            f"filter((lambda a: {self.filter_}), {self.source})",
            {},
            {"self": self},
        )
        _check_type(attachments, _Generator[T, None, None])
        return attachments

    # validators
    @_validates("source")
    def _validate_source(self, _, source: str):
        if not source.startswith("self."):
            raise ValueError("Illegal source")

    @_validates("attachments_type_name")
    def _validate_attachments_type_name(self, _, name: str):
        if name not in globals():
            raise ValueError("Illegal attachments type name")


class DefaultActor(_Base):
    __tablename__ = "DefaultActor"

    """
    Virtual actors
    """

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    actor_id = _Column(
        _Int, _Fk("Actor.id"), index=True, unique=True, nullable=False
    )
    name = _Column(_Str, unique=True, index=True)

    # relationships
    actor: _Map["Actor"] = _rel(back_populates="default_actor")
    task_delegations: _Map[_List["DefaultActorTaskDelegation"]] = _rel(
        back_populates="default_actor"
    )
    restaurant: _Map[_Opt["Restaurant"]] = _rel(back_populates="default_actor")
    restaurant_external_department: _Map[
        _Opt["RestaurantExternalDepartment"]
    ] = _rel(back_populates="default_actor")
    restaurant_internal_department: _Map[
        _Opt["RestaurantInternalDepartment"]
    ] = _rel(back_populates="default_actor")


class TaskType(_Base):
    __tablename__ = "TaskType"

    """
    Task templates
    """

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    name = _Column(_Str, unique=True, index=True)

    # relationships
    restaurant_employee_position_access_levels: _Map[
        _List["RestaurantEmployeePositionAccessLevel"]
    ] = _rel(back_populates="task_type")
    personal_access_levels: _Map[_List["ActorAccessLevel"]] = _rel(
        back_populates="task_type"
    )
    groups: _Map[_List["TaskTypeGroupTask"]] = _rel(back_populates="type")
    incoming_in_task_delegations: _Map[
        _List["DefaultActorTaskDelegation"]
    ] = _rel(back_populates="incoming_task_type")
    outcoming_in_task_delegations: _Map[
        _List["DefaultActorTaskDelegation"]
    ] = _rel(back_populates="outcoming_task_type")


class TaskTypeGroup(_Base):
    __tablename__ = "TaskTypeGroup"

    id = _Column(_Int, primary_key=True, index=True)
    name = _Column(_Str, unique=True, index=True, nullable=False)

    types: _Map[_List["TaskTypeGroupTask"]] = _rel(back_populates="group")


class TaskTypeGroupTask(_Base):
    __tablename__ = "TaskTypeGroupTask"

    group_id = _Column(_Int, _Fk("TaskTypeGroup.id"), primary_key=True)
    type_id = _Column(_Int, _Fk("TaskType.id"), primary_key=True)

    group: _Map["TaskTypeGroup"] = _rel(back_populates="types")
    type: _Map["TaskType"] = _rel(back_populates="groups")

    # composite primary key
    __table_args__ = (_PKConstraint(group_id, type_id), {})


class ActorAccessLevel(_Base):
    __tablename__ = "ActorAccessLevel"

    """
    Personal access level issued by another actor
    """

    # columns
    id = _Column(_Int, primary_key=True)
    actor_id = _Column(_Int, _Fk("Actor.id"), nullable=False, index=True)
    task_type_id = _Column(
        _Int, _Fk("TaskType.id"), nullable=False, index=True
    )
    task_target_id = _Column(
        _Int, _Fk("TaskTarget.id"), index=True, unique=True
    )
    role = _Column(_Str, nullable=False, index=True)

    # relationships
    actor: _Map["Actor"] = _rel(back_populates="personal_access_levels")
    task_type: _Map["TaskType"] = _rel(back_populates="personal_access_levels")
    task_target: _Map["TaskTarget"] = _rel(
        back_populates="defining_access_level"
    )


class TaskTarget(_Base):
    __tablename__ = "TaskTarget"

    """
    Action for which the task was created
    """

    # columns
    id = _Column(_Int, primary_key=True, index=True)

    # relationships
    task: _Map["Task"] = _rel(back_populates="target")
    types: _Map[_List["TaskTargetTypeTarget"]] = _rel(back_populates="target")
    supply: _Map[_Opt["Supply"]] = _rel(back_populates="task_target")
    salary: _Map[_Opt["Salary"]] = _rel(back_populates="task_target")
    writeoff: _Map[_Opt["WriteOff"]] = _rel(back_populates="task_target")
    customer_order: _Map[_Opt["CustomerOrder"]] = _rel(
        back_populates="task_target"
    )
    customer_payment: _Map[_Opt["CustomerPayment"]] = _rel(
        back_populates="task_target"
    )
    supply_order: _Map[_Opt["SupplyOrder"]] = _rel(
        back_populates="task_target"
    )
    supply_payment: _Map[_Opt["SupplyPayment"]] = _rel(
        back_populates="task_target"
    )
    defining_access_level: _Map[_Opt["ActorAccessLevel"]] = _rel(
        back_populates="task_target"
    )
    discount_group: _Map[_Opt["DiscountGroup"]] = _rel(
        back_populates="task_target"
    )
    dicsount: _Map[_Opt["Discount"]] = _rel(back_populates="task_target")


class TaskTargetType(_Base):
    __tablename__ = "TaskTargetType"

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    name = _Column(_Str, nullable=False, unique=True, index=True)

    # relationships
    targets: _Map[_List["TaskTargetTypeTarget"]] = _rel(back_populates="type")


class TaskTargetTypeTarget(_Base):
    __tablename__ = "TaskTargetTypeTarget"

    # columns
    type_id = _Column(_Int, _Fk("TaskTargetType.id"), primary_key=True)
    target_id = _Column(_Int, _Fk("TaskTarget.id"), primary_key=True)

    type: _Map["TaskTargetType"] = _rel(back_populates="targets")
    target: _Map["TaskTarget"] = _rel(back_populates="types")


class SubTask(_Base):
    __tablename__ = "SubTask"

    """
    A subtask created by the executor of the main task to complete it
    """

    # columns
    child_id = _Column(_Int, _Fk("Task.id"), primary_key=True)
    parent_id = _Column(_Int, _Fk("Task.id"), primary_key=True)
    priority = _Column(_Int, nullable=False, default=0)

    # relationships
    subtasks: _Map[_List["Task"]] = _rel(back_populates="parent")
    parent: _Map["Task"] = _rel(back_populates="subtasks")

    # composite primary key
    __table_args__ = (_PKConstraint(child_id, parent_id), {})


class User(_Base):
    __tablename__ = "User"

    """
    People (real actor)
    """

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    hashed_password = _Column(_Str, nullable=False)
    actor_id = _Column(_Int, _Fk("Actor.id"), nullable=False, index=True)
    role = _Column(_Str, nullable=False, index=True)
    email = _Column(_Str, unique=True, index=True, nullable=False)
    phone = _Column(_Int, unique=True, index=True)
    telegram = _Column(_Int, unique=True, index=True)
    lname = _Column(_Str)
    fname = _Column(_Str, nullable=False)
    sname = _Column(_Str)
    gender = _Column(_Bool)
    address = _Column(_Str)
    last_online = _Column(_Dt, nullable=False, default=_dt.utcnow, index=True)
    created = _Column(_Dt, nullable=False, index=True)
    deleted = _Column(_Dt)

    # relationships
    actor: _Map["Actor"] = _rel(back_populates="user")
    restaurant_employee: _Map[_Opt["RestaurantEmployee"]] = _rel(
        back_populates="user"
    )
    customer: _Map[_Opt["Customer"]] = _rel(back_populates="user")
    verifications: _Map[_List["Verification"]] = _rel(back_populates="user")

    # methods
    def verify_password(self, password: str) -> bool:
        return _hash.bcrypt.verify(
            password, self.hashed_password  # pyright: ignore
        )


class Verification(_Base):
    __tablename__ = "Verification"

    """
    User contact data awaiting confirmaion
    """

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    user_id = _Column(_Int, _Fk("User.id"), nullable=False, index=True)
    field_name = _Column(_Str, nullable=False)
    value = _Column(_Str, nullable=False, unique=True)

    # relationships
    user: _Map["User"] = _rel(back_populates="verifications")


class RestaurantEmployeePosition(_Base):
    __tablename__ = "RestaurantEmployeePosition"

    """
    Job title
    """

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    name = _Column(_Str, unique=True, nullable=False, index=True)
    salary = _Column(_Float, nullable=False)
    expierence_coefficient = _Column(_Float, nullable=False, default=1)

    # relationships
    employees: _Map[_List["RestaurantEmployee"]] = _rel(
        back_populates="position"
    )
    access_levels: _Map[_List["RestaurantEmployeePositionAccessLevel"]] = _rel(
        back_populates="position"
    )


class RestaurantEmployeePositionAccessLevel(_Base):
    __tablename__ = "RestaurantEmployeePositionAccessLevel"

    """
    Group access levels for all restaurant employees in a specified position
    """

    # columns
    position_id = _Column(
        _Int, _Fk("RestaurantEmployeePosition.id"), primary_key=True
    )
    task_type_group_id = _Column(
        _Int, _Fk("TaskTypeGroup.id"), primary_key=True
    )
    role = _Column(_Str, nullable=False, index=True)

    # relationships
    position: _Map["RestaurantEmployeePosition"] = _rel(
        back_populates="access_levels"
    )
    task_type_group: _Map["TaskTypeGroup"] = _rel(
        back_populates="restaurant_employee_position_access_levels"
    )

    # composite primary key
    __table_args__ = (_PKConstraint(position_id, task_type_group_id), {})


class RestaurantEmployee(_Base):
    __tablename__ = "RestaurantEmployee"

    """
    Base model for each restaurant employee
    """

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    user_id = _Column(_Int, _Fk("User.id"), nullable=False, unique=True)
    hiring_date = _Column(_Dt, nullable=False)
    fired_date = _Column(_Dt)
    on_shift = _Column(_Bool, nullable=False, index=True)
    position_id = _Column(
        _Int, _Fk("RestaurantEmployeePosition.id"), nullable=False, index=True
    )
    restaurant_id = _Column(_Int, _Fk("Restaurant.id"), index=True)

    # relationships
    user: _Map["User"] = _rel(back_populates="restaurant_employee")
    position: _Map["RestaurantEmployeePosition"] = _rel(
        back_populates="employees"
    )
    salaries: _Map[_List["Salary"]] = _rel(
        back_populates="restaurant_employee"
    )
    restaurant: _Map["Restaurant"] = _rel(back_populates="employees")


class Customer(_Base):
    __tablename__ = "Customer"

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    user_id = _Column(
        _Int, _Fk("User.id"), nullable=False, unique=True, index=True
    )
    bonus_points = _Column(_Float, nullable=False, default=0)

    # relationships
    user: _Map["User"] = _rel(back_populates="customer")
    favorites: _Map[_List["CustomerFavoriteProduct"]] = _rel(
        back_populates="customer"
    )
    shopping_cart_products: _Map[_List["CustomerFavoriteProduct"]] = _rel(
        back_populates="customer"
    )


class Material(_Base):
    __tablename__ = "Material"

    """
    Supplied consumables
    """

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    item_id = _Column(
        _Int, _Fk("Item.id"), unique=True, nullable=False, index=True
    )
    name = _Column(_Str, unique=True, nullable=False, index=True)
    unit = _Column(_Str, nullable=False)
    price = _Column(_Float, nullable=False)
    best_before = _Column(_Dt)
    group_id = _Column(_Int, _Fk("MaterialGroup.id"), nullable=False)
    created = _Column(_Dt, nullable=False)

    # relationships
    item: _Map["Item"] = _rel(back_populates="material")
    group: _Map["MaterialGroup"] = _rel(back_populates="materials")
    ingridients: _Map[_List["IngridientMaterial"]] = _rel(
        back_populates="material"
    )
    allergic_flags: _Map[_List["MaterialAllergicFlag"]] = _rel(
        back_populates="material"
    )
    stock_balance: _Map[_List["MaterialStockBalance"]] = _rel(
        back_populates="material"
    )


class MaterialStockBalance(_Base):
    __tablename__ = "MaterialStockBalance"

    # columns
    material_id = _Column(_Int, _Fk("Material.id"), primary_key=True)
    restaurant_id = _Column(_Int, _Fk("Restaurant.id"), primary_key=True)
    balance = _Column(_Float, nullable=True)

    # relationships
    material: _Map["Material"] = _rel(back_populates="stock_balance")
    restaurant: _Map["Restaurant"] = _rel(back_populates="stock_balance")

    # composite primary key
    __table_args__ = (_PKConstraint(material_id, restaurant_id), {})


class MaterialGroup(_Base):
    __tablename__ = "MaterialGroup"

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    name = _Column(_Str, nullable=False, unique=True, index=True)

    # relationships
    parent_group: _Map[_Opt["MaterialSubGroup"]] = _rel(back_populates="child")
    subgroups: _Map[_List["MaterialSubGroup"]] = _rel(back_populates="parent")


class MaterialSubGroup(_Base):
    __tablename__ = "MaterialSubGroup"

    # columns
    parent_id = _Column(_Int, _Fk("MaterialGroup.id"), primary_key=True)
    child_id = _Column(_Int, _Fk("MaterialGroup.id"), primary_key=True)

    # relationships
    parent: _Map["MaterialGroup"] = _rel(back_populates="subgroups")
    child: _Map["MaterialGroup"] = _rel(back_populates="parent_group")

    # composite primary key
    __table_args__ = (_PKConstraint(child_id, parent_id), {})


class Supply(_Base):
    __tablename__ = "Supply"

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    restaurant_id = _Column(
        _Int, _Fk("Restaurant.id"), nullable=False, index=True
    )
    task_target_id = _Column(
        _Int, _Fk("TaskTarget.id"), nullable=False, index=True
    )

    # relationships
    task_target: _Map["TaskTarget"] = _rel(back_populates="supply")
    items: _Map[_List["SupplyItem"]] = _rel(back_populates="supply")
    payment: _Map["SupplyPayment"] = _rel(back_populates="supply")


class SupplyItem(_Base):
    __tablename__ = "SupplyItem"

    # columns
    supply_id = _Column(_Int, _Fk("Supply.id"), primary_key=True)
    item_id = _Column(_Int, _Fk("Item.id"), primary_key=True)
    count = _Column(_Float, nullable=False)
    price = _Column(_Float, nullable=True)

    # relationships
    supply: _Map["Supply"] = _rel(back_populates="items")
    item: _Map["Item"] = _rel(back_populates="supplies")

    # composite primary key
    __table_args__ = (_PKConstraint(supply_id, item_id), {})


class Ingridient(_Base):
    __tablename__ = "Ingridient"

    """
    Ingredient displayed in the dish composition
    """

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    name = _Column(_Str, unique=True, nullable=False, index=True)
    calories = _Column(_Float, nullable=False)
    fats = _Column(_Float, nullable=False)
    proteins = _Column(_Float, nullable=False)
    carbohidrates = _Column(_Float, nullable=False)
    created = _Column(_Dt, nullable=False)

    # relationships
    materials: _Map[_List["IngridientMaterial"]] = _rel(
        back_populates="ingridient"
    )
    products: _Map[_List["ProductIngridient"]] = _rel(
        back_populates="ingridient"
    )
    available_to_add_in_products: _Map[
        _List["ProductAvailableExtraIngridient"]
    ] = _rel(back_populates="ingridient")


class IngridientMaterial(_Base):
    __tablename__ = "IngridientMaterial"

    """
    Consumables that make up the ingredient
    """

    # columns
    material_id = _Column(_Int, _Fk("Material.id"), primary_key=True)
    ingridient_id = _Column(_Int, _Fk("Ingridient.id"), primary_key=True)
    im_ratio = _Column(_Float, nullable=False)

    # relationships
    material: _Map["Material"] = _rel(back_populates="ingridients")
    ingridient: _Map["Ingridient"] = _rel(back_populates="materials")

    # composite primary key
    __table_args__ = (_PKConstraint(ingridient_id, material_id), {})


class Product(_Base):
    __tablename__ = "Product"

    """
    Item in the menu
    """

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    name = _Column(_Str, nullable=False, unique=True, index=True)
    price = _Column(_Float)
    sale = _Column(_Float)
    best_before = _Column(_Dt)
    status = _Column(_Str, nullable=False, index=True)
    own_production = _Column(_Bool, nullable=False)
    avaible_in_online_order = _Column(_Bool, nullable=False, index=True)
    tare_id = _Column(_Int, _Fk("Tare.id"), nullable=True)

    # relationships
    ingridients: _Map[_List["ProductIngridient"]] = _rel(
        back_populates="product"
    )
    customers_who_added_to_favorites: _Map[
        _List["CustomerFavoriteProduct"]
    ] = _rel(back_populates="product")
    customers_who_added_to_shopping_cart: _Map[
        _List["CustomerShoppingCartProduct"]
    ] = _rel(back_populates="product")
    customer_orders: _Map[_List["CustomerOrderProduct"]] = _rel(
        back_populates="product"
    )
    available_extra_ingridients: _Map[
        _List["ProductAvailableExtraIngridient"]
    ] = _rel(back_populates="product")
    category: _Map["ProductCategoryProduct"] = _rel(back_populates="product")
    discounts: _Map[_List["DiscountOptionProduct"]] = _rel(
        back_populates="product"
    )
    tare: _Map[_Opt["Tare"]] = _rel(back_populates="products")
    restaurants: _Map[_List["RestaurantProduct"]] = _rel(
        back_populates="product"
    )


class RestaurantProduct(_Base):
    __tablename__ = "RestaurantProduct"

    """
    Product selling in a restaurant
    """

    product_id = _Column(_Int, _Fk("Product.id"), primary_key=True)
    restaurant_id = _Column(_Int, _Fk("Restaurant.id"), primary_key=True)
    suspended = _Column(_Bool, nullable=False, default=False, index=True)

    product: _Map["Product"] = _rel(back_populates="restaurants")
    restaurant: _Map["Restaurant"] = _rel(back_populates="products")

    __table_args__ = (_PKConstraint(restaurant_id, product_id), {})


class ProductIngridient(_Base):
    __tablename__ = "ProductIngridient"

    """
    Product composition with information on possible customization
    """

    # columns
    product_id = _Column(_Int, _Fk("Product.id"), primary_key=True)
    ingridient_id = _Column(_Int, _Fk("Ingridient.id"), primary_key=True)
    ip_ratio = _Column(_Float, nullable=False)
    editable = _Column(_Bool, nullable=False)
    edit_price = _Column(_Float)
    max_change = _Column(_Float)

    # relationships
    product: _Map["Product"] = _rel(back_populates="ingridients")
    ingridient: _Map["Ingridient"] = _rel(back_populates="products")

    # composite primary key
    __table_args__ = (_PKConstraint(ingridient_id, product_id), {})


class CustomerFavoriteProduct(_Base):
    __tablename__ = "CustomerFavoriteProduct"

    """
    Product in user's favorites
    """

    # columns
    customer_id = _Column(_Int, _Fk("Customer.id"), primary_key=True)
    product_id = _Column(_Int, _Fk("Product.id"), primary_key=True)

    # relationships
    customer: _Map["Customer"] = _rel(back_populates="favorite_products")
    product: _Map["Product"] = _rel(
        back_populates="cusomers_who_added_to_favorites"
    )

    # composite primary key
    __table_args__ = (_PKConstraint(customer_id, product_id), {})


class CustomerShoppingCartProduct(_Base):
    __tablename__ = "CustomerShoppingCartProduct"

    """
    Product in user shopping cart
    """

    # columns
    customer_id = _Column(_Int, _Fk("Customer.id"), primary_key=True)
    product_id = _Column(_Int, _Fk("Product.id"), primary_key=True)
    count = _Column(_Int, nullable=False, default=1)

    # relationships
    customer: _Map["Customer"] = _rel(back_populates="shopping_cart_products")
    product: _Map["Product"] = _rel(
        back_populates="customers_who_added_to_shopping_cart"
    )

    # composite primary key
    __table_args__ = (_PKConstraint(customer_id, product_id), {})


class CustomerOrder(_Base):
    __tablename__ = "CustomerOrder"

    """
    Order made via website or waiter's terminal
    """

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    task_target_id = _Column(
        _Int, _Fk("TaskTarget.id"), nullable=False, unique=False, index=True
    )
    restaurant_id = _Column(
        _Int, _Fk("Restaurant.id"), nullable=False, index=True
    )
    status = _Column(_Str, nullable=False)

    # relationships
    task_target: _Map["TaskTarget"] = _rel(back_populates="customer_order")
    products: _Map[_List["CustomerOrderProduct"]] = _rel(
        back_populates="customer_order"
    )
    online_order: _Map[_Opt["OnlineOrder"]] = _rel(
        back_populates="customer_order"
    )
    waiter_order: _Map[_Opt["WaiterOrder"]] = _rel(
        back_populates="customer_order"
    )
    payment: _Map["CustomerPayment"] = _rel(back_populates="order")
    restaurant: _Map["Restaurant"] = _rel(back_populates="customer_orders")


class CustomerOrderProduct(_Base):
    __tablename__ = "CustomerOrderProduct"

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    order_id = _Column(
        _Int, _Fk("CustomerOrder.id"), nullable=False, index=True
    )
    product_id = _Column(_Int, _Fk("Product.id"), nullable=False, index=True)
    discount_option_id = _Column(_Int, _Fk("DiscountOption.id"), nullable=True)
    paid_by_bonus_points = _Column(_Bool, nullable=False, default=False)
    count = _Column(_Int, nullable=False, default=1)

    # relationships
    customer_order: _Map["CustomerOrder"] = _rel(back_populates="products")
    product: _Map["Product"] = _rel(back_populates="customer_orders")
    discount_option: _Map[_Opt["DiscountOption"]] = _rel(
        back_populates="order_products"
    )


class OnlineOrder(_Base):
    __tablename__ = "OnlineOrder"

    """
    Purchase on the website
    """

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    order_id = _Column(
        _Int, _Fk("CustomerOrder.id"), nullable=False, index=True, unique=True
    )

    # relationships
    customer_order: _Map["CustomerOrder"] = _rel(back_populates="online_order")


class ProductAvailableExtraIngridient(_Base):
    __tablename__ = "ProductAvailableExtraIngridient"

    """
    Ingridients that can be added to a product
    """

    # columns
    product_id = _Column(_Int, _Fk("Product.id"), primary_key=True)
    ingridient_id = _Column(_Int, _Fk("Ingridient.id"), primary_key=True)
    price = _Column(_Float, nullable=False)

    # relationships
    product: _Map["Product"] = _rel(
        back_populates="available_extra_ingridients"
    )
    ingridient: _Map["Ingridient"] = _rel(
        back_populates="available_to_add_in_products"
    )

    # composite primary key
    __table_args__ = (_PKConstraint(ingridient_id, product_id), {})


class CustomerOrderProductIngridientChange(_Base):
    __tablename__ = "CustomerOrderProductIngridientChange"

    """
    Customized ingridients in order
    """

    # columns
    order_product_id = _Column(
        _Int, _Fk("CustomerOrderProduct.id"), primary_key=True
    )
    ingridient_id = _Column(_Int, _Fk("Ingridient.id"), primary_key=True)
    ip_ratio_change = _Column(_Float, nullable=False)

    # relationships
    order_product: _Map["CustomerOrderProduct"] = _rel(
        back_populates="changed_ingridients"
    )
    ingridient: _Map["Ingridient"] = _rel(
        back_populates="changed_in_order_products"
    )

    # composite primary key
    __table_args__ = (_PKConstraint(ingridient_id, order_product_id), {})


class CustomerOrderProductExtraIngridient(_Base):
    __tablename__ = "CustomerOrderExtraIngridient"

    """
    Extra ingridients in order
    """

    # columns
    order_product_id = _Column(
        _Int, _Fk("CustomerOrderProduct.id"), primary_key=True
    )
    ingridient_id = _Column(_Int, _Fk("Ingridient.id"), primary_key=True)
    count = _Column(_Int, nullable=False, default=1)

    # relationships
    order_product: _Map["CustomerOrderProduct"] = _rel(
        back_populates="extra_ingridients"
    )
    ingridient: _Map["Ingridient"] = _rel(
        back_populates="added_to_order_products"
    )

    # composite primary key
    __table_args__ = (_PKConstraint(ingridient_id, order_product_id), {})


class Table(_Base):
    __tablename__ = "Table"

    """
    Table in a restaurant
    """

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    number = _Column(_Int, nullable=False, index=True)
    location_id = _Column(
        _Int, _Fk("TableLocation.id"), nullable=False, index=True
    )

    # relationships
    location: _Map["TableLocation"] = _rel(back_populates="tables")
    waiter_orders: _Map[_List["WaiterOrder"]] = _rel(back_populates="table")


class TableLocation(_Base):
    __tablename__ = "TableLocation"

    """
    Location with tables (floor, roof, etc.)
    """

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    name = _Column(_Str, unique=True, index=True, nullable=False)
    restaurant_id = _Column(
        _Int, _Fk("Restaurant.id"), nullable=False, index=True
    )

    # relationships
    tables: _Map[_List["Table"]] = _rel(back_populates="location")
    restaurant: _Map["Restaurant"] = _rel(back_populates="table_locations")


class WaiterOrder(_Base):
    __tablename__ = "WaiterOrder"

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    table_id = _Column(_Int, _Fk("Table.id"), nullable=False)
    order_Id = _Column(
        _Int, _Fk("CustomerOrder.id"), nullable=False, unique=True, index=True
    )

    # relationships
    table: _Map["Table"] = _rel(back_populates="waiter_orders")
    customer_order: _Map["CustomerOrder"] = _rel(back_populates="waiter_order")


class Salary(_Base):
    __tablename__ = "Salary"

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    task_target_id = _Column(
        _Int, _Fk("TaskTarget.id"), nullable=False, unique=True, index=True
    )
    restaurant_employee_id = _Column(
        _Int, _Fk("RestaurantEmployee.id"), nullable=False, index=True
    )
    bonus = _Column(_Float)

    # relationships
    task_target: _Map["TaskTarget"] = _rel(back_populates="salary")
    restaurant_employee: _Map["RestaurantEmployee"] = _rel(
        back_populates="salaries"
    )


class AllergicFlag(_Base):
    __tablename__ = "AllergicFlag"

    """
    Possible options for risk groups and allergies
    """

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    name = _Column(_Str, unique=True, index=True, nullable=False)

    # relationships
    materials: _Map[_List["MaterialAllergicFlag"]] = _rel(
        back_populates="allergic_flag"
    )


class MaterialAllergicFlag(_Base):
    __tablename__ = "MaterialAllergicFlag"

    """
    Allergic flags of the consumable
    """

    # columns
    material_id = _Column(_Int, _Fk("Material.id"), primary_key=True)
    flag_id = _Column(_Int, _Fk("AllergicFlag.id"), primary_key=True)

    # relationships
    material: _Map["Material"] = _rel(back_populates="allergic_flags")
    allergic_flag: _Map["AllergicFlag"] = _rel(back_populates="materials")

    # composite primary key
    __table_args__ = (_PKConstraint(material_id, flag_id), {})


class ProductCategory(_Base):
    __tablename__ = "ProductCategory"

    """
    Menu section
    """

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    name = _Column(_Str, unique=True, index=True, nullable=False)

    # relationships
    products: _Map[_List["ProductCategoryProduct"]] = _rel(
        back_populates="product_category"
    )


class ProductCategoryProduct(_Base):
    __tablename__ = "ProductCategoryProduct"

    # columns
    product_id = _Column(_Int, _Fk("Product.id"), primary_key=True)
    category_id = _Column(_Int, _Fk("ProductCategory.id"), primary_key=True)

    # relationships
    product: _Map["Product"] = _rel(back_populates="category")
    product_category: _Map["ProductCategory"] = _rel(back_populates="products")

    # composite primary key
    __table_args__ = (_PKConstraint(product_id, category_id), {})


class CustomerPayment(_Base):
    __tablename__ = "CustomerPayment"

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    order_id = _Column(
        _Int, _Fk("CustomerOrder.id"), unique=True, nullable=False, index=True
    )
    task_target_id = _Column(
        _Int, _Fk("TaskTarget.id"), nullable=False, index=True, unique=True
    )

    # relationships
    order: _Map["CustomerOrder"] = _rel(back_populates="payment")
    task_target: _Map["TaskTarget"] = _rel(back_populates="customer_payment")


class DiscountGroup(_Base):
    __tablename__ = "DiscountGroup"

    """
    Named menu section with promotional items
    """

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    name = _Column(_Str, nullable=False)
    task_target_id = _Column(
        _Int, _Fk("TaskTarget.id"), index=True, unique=True, nullable=False
    )

    # relationships
    task_target: _Map["TaskTarget"] = _rel(back_populates="discount_group")
    discounts: _Map[_List["Discount"]] = _rel(back_populates="group")


class Discount(_Base):
    __tablename__ = "Discount"

    """
    Single promotional offer
    """

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    promocode = _Column(_Str, nullable=True, index=True, unique=True)
    group_id = _Column(
        _Int, _Fk("DiscountGroup.id"), nullable=False, index=True
    )
    delivery_only = _Column(_Bool, nullable=False, index=True, default=False)
    name = _Column(_Str, index=True, nullable=False)
    description = _Column(_Str, nullable=True)
    condition = _Column(_Str, nullable=True)
    value = _Column(_Str, nullable=False)
    task_target_id = _Column(
        _Int, _Fk("TaskTarget.id"), nullable=False, unique=True
    )

    # relationships
    task_target: _Map["TaskTarget"] = _rel(back_populates="discount")
    group: _Map["DiscountGroup"] = _rel(back_populates="discounts")
    options: _Map[_List["DiscountOption"]] = _rel(back_populates="discount")
    restaurants: _Map[_List["RestaurantDiscount"]] = _rel(
        back_populates="discount"
    )


class RestaurantDiscount(_Base):
    __tablename__ = "RestaurantDiscount"

    """
    Discounts offered in a restaurant
    """

    # columns
    restaurant_id = _Column(_Int, _Fk("Restaurant.id"), primary_key=True)
    discount_id = _Column(_Int, _Fk("Discount.id"), primary_key=True)

    # relationships
    restaurant: _Map["Restaurant"] = _rel(back_populates="discounts")
    discount: _Map["Discount"] = _rel(back_populates="restaurants")

    # composite primary key
    __table_args__ = (_PKConstraint(restaurant_id, discount_id), {})


class CustomerOrderDiscount(_Base):
    __tablename__ = "CustomerOrderDiscount"

    """
    Discounts used in order
    """

    # columns
    customer_order_id = _Column(
        _Int, _Fk("CustomerOrder.id"), primary_key=True
    )
    discount_id = _Column(_Int, _Fk("Discount.id"), primary_key=True)

    # relationshis
    customer_order: _Map["CustomerOrder"] = _rel(back_populates="discounts")
    discount: _Map["Discount"] = _rel(back_populates="orders")


class DiscountOption(_Base):
    __tablename__ = "DiscountOption"

    """
    A set of products from which you can choose one to participate
    in the promotion.
    """

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    title = _Column(_Str, nullable=True)
    discount_id = _Column(_Int, _Fk("Discount.id"), nullable=False)

    # relationships
    discount: _Map["Discount"] = _rel(back_populates="options")
    products: _Map["DiscountOptionProduct"] = _rel(back_populates="option")


class DiscountOptionProduct(_Base):
    __tablename__ = "DiscountOptionProduct"

    """
    Product that can be selected from the list as option to participate
    in the promotion
    """

    # columns
    discount_option_id = _Column(
        _Int, _Fk("DiscountOption.id"), primary_key=True
    )
    product_id = _Column(_Int, _Fk("Product.id"), primary_key=True)

    # relationships
    option: _Map["DiscountOption"] = _rel(back_populates="products")
    product: _Map["Product"] = _rel(back_populates="discounts")


class SupplyOrder(_Base):
    __tablename__ = "SupplyOrder"

    """
    Order for the supply
    """

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    task_target_id = _Column(
        _Int, _Fk("TaskTarget.id"), index=True, nullable=False, unique=True
    )

    # relationships
    task_target: _Map["TaskTarget"] = _rel(back_populates="supply_order")
    items: _Map[_List["SupplyOrderItem"]] = _rel(
        back_populates="kitchen_order"
    )


class SupplyOrderItem(_Base):
    __tablename__ = "SupplyOrderItem"

    # columns
    supply_order_id = _Column(_Int, _Fk("SupplyOrder.id"), primary_key=True)
    item_id = _Column(_Int, _Fk("Item.id"), primary_key=True)
    count = _Column(_Float, nullable=False)

    # relationships
    supply_order: _Map["SupplyOrder"] = _rel(back_populates="items")
    item: _Map["Item"] = _rel(back_populates="supply_orders")

    # composite primary key
    __table_args__ = (_PKConstraint(supply_order_id, item_id), {})


class WriteOffReason(_Base):
    __tablename__ = "WriteOffReason"

    """
    Write-off act (the reason why consumables can be written off)
    """

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    name = _Column(_Str, unique=True, nullable=False, index=True)
    descritption = _Column(_Str)
    group_id = _Column(_Int, _Fk("WriteOffReasonGroup.id"), nullable=False)

    # relationships
    group: _Map["WriteOffReasonGroup"] = _rel(back_populates="reasons")
    writeoffs: _Map[_List["WriteOff"]] = _rel(back_populates="reason")


class WriteOffReasonGroup(_Base):
    __tablename__ = "WriteOffReasonGroup"

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    name = _Column(_Str, unique=True, nullable=False, index=True)
    description = _Column(_Str, nullable=False, default="")

    # relationships
    reasons: _Map[_List["WriteOffReason"]] = _rel(back_populates="group")


class WriteOff(_Base):
    __tablename__ = "WriteOff"

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    task_target_id = _Column(
        _Int, _Fk("TaskTarget.id"), nullable=False, index=True, unique=True
    )
    reason_id = _Column(
        _Int, _Fk("WriteOffReason.id"), nullable=False, index=True
    )

    # relationships
    task_target: _Map["TaskTarget"] = _rel(back_populates="writeoff")
    reason: _Map["WriteOffReason"] = _rel(back_populates="writeoffs")
    items: _Map[_List["WriteOffItem"]] = _rel(back_populates="writeoff")


class WriteOffItem(_Base):
    __tablename__ = "WriteOffItem"

    # columns
    writeoff_id = _Column(_Int, _Fk("WriteOff.id"), primary_key=True)
    item_id = _Column(_Int, _Fk("Item.id"), primary_key=True)
    count = _Column(_Float, nullable=False)

    # relationshils
    writeoff: _Map["WriteOff"] = _rel(back_populates="materials")
    item: _Map["Item"] = _rel(back_populates="writeoffs")

    # composite primary key
    __table_args__ = (_PKConstraint(writeoff_id, item_id), {})


class SupplyPayment(_Base):
    __tablename__ = "SupplyPayment"

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    task_target_id = _Column(
        _Int, _Fk("TaskTarget.id"), index=True, unique=True, nullable=False
    )
    supply_id = _Column(
        _Int, _Fk("Supply.id"), index=True, unique=True, nullable=False
    )

    # relationships
    task_target: _Map["TaskTarget"] = _rel(back_populates="supply_payment")
    supply: _Map["Supply"] = _rel(back_populates="payment")


class Tare(_Base):
    __tablename__ = "Tare"

    """
    Packaging for delivered products
    """

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    item_id = _Column(
        _Int, _Fk("Item.id"), unique=True, nullable=False, index=True
    )
    name = _Column(_Str, nullable=False)
    price = _Column(_Float, nullable=True)
    stock_balance = _Column(_Int, nullable=True)

    # relationships
    item: _Map["Item"] = _rel(back_populates="tare")
    products: _Map[_List["Product"]] = _rel(back_populates="tare")


class Inventory(_Base):
    __tablename__ = "Inventory"

    """
    Reestaraunt property
    """

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    item_id = _Column(
        _Int, _Fk("Item.id"), unique=True, nullable=False, index=True
    )
    name = _Column(_Str, nullable=False, unique=True)
    description = _Column(_Str, nullable=False)
    group_id = _Column(_Int, _Fk("InventoryGroup.id"), nullable=False)

    # relationships
    item: _Map["Item"] = _rel(back_populates="inventory")
    group: _Map["InventoryGroup"] = _rel(back_populates="inventory")


class InventoryGroup(_Base):
    __tablename__ = "InventoryGroup"

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    name = _Column(_Str, nullable=False, unique=True)

    # relationships
    inventory: _Map[_List["Inventory"]] = _rel(back_populates="group")
    subgroups: _Map[_List["InventorySubGroup"]] = _rel(back_populates="parent")
    parent_group: _Map[_Opt["InventorySubGroup"]] = _rel(
        back_populates="child"
    )


class InventorySubGroup(_Base):
    __tablename__ = "InventorySubGroup"

    # columns
    parent_id = _Column(_Int, _Fk("InventoryGroup.id"), primary_key=True)
    child_id = _Column(_Int, _Fk("InventoryGroup.id"), primary_key=True)

    # relationships
    parent: _Map["InventoryGroup"] = _rel(back_populates="subgroups")
    child: _Map["InventoryGroup"] = _rel(back_populates="parent_group")

    # composite primary key
    __table_args__ = (_PKConstraint(parent_id, child_id), {})


class Item(_Base):
    __tablename__ = "Item"

    """
    Any company property that is used to operate a restaurant and prepare food.
    """

    # columns
    id = _Column(_Int, primary_key=True, index=True)

    # relationships
    material: _Map[_Opt["Material"]] = _rel(back_populates="item")
    tare: _Map[_Opt["Tare"]] = _rel(back_populates="item")
    inventory: _Map[_Opt["Inventory"]] = _rel(back_populates="item")
    writeoffs: _Map[_List["WriteOffItem"]] = _rel(back_populates="item")
    supply_orders: _Map[_List["SupplyOrder"]] = _rel(back_populates="item")


class Task(_Base):
    __tablename__ = "Task"

    """
    The main object required to perform financially responsible tasks
    """

    # columns
    id = _Column(_Int, primary_key=True, index=True)
    name = _Column(_Str, nullable=False)
    comment = _Column(_Str)
    status = _Column(_Str, nullable=False, index=True)
    target_id = _Column(_Int, _Fk("TaskTarget.id"), nullable=False, index=True)
    created = _Column(_Dt, nullable=False, default=_dt.utcnow, index=True)
    author_id = _Column(_Int, _Fk("Actor.id"), nullable=False, index=True)
    changed = _Column(_Bool, nullable=False, default=False)
    start_execution = _Column(_Dt, index=True)
    execution_started = _Column(_Dt)
    fail_on_late_start = _Column(_Bool, nullable=False, default=False)
    complete_before = _Column(_Dt)
    completed = _Column(_Dt)
    fail_on_late_complete = _Column(_Bool, nullable=False, default=False)
    executor_id = _Column(_Int, _Fk("Actor.id"), nullable=False, index=True)
    approved = _Column(_Dt, index=True)
    inspector_id = _Column(_Int, _Fk("Actor.id"), nullable=False, index=True)

    # relationships
    task_type: _Map["TaskType"] = _rel(back_populates="tasks")
    target: _Map["TaskTarget"] = _rel(back_populates="task")
    author: _Map["Actor"] = _rel(back_populates="created_tasks")
    executor: _Map["Actor"] = _rel(back_populates="tasks_to_execute")
    inspector: _Map["Actor"] = _rel(back_populates="tasks_to_inspect")
    parent: _Map[_Opt["SubTask"]] = _rel(back_populates="subtasks")
    subtasks: _Map[_List["SubTask"]] = _rel(back_populates="parent")

    # methods
    @property
    def is_started_late(self) -> bool:
        if not self.start_execution:  # pyright: ignore
            return False
        elif (
            not self.execution_started  # pyright: ignore
            and self.start_execution <= _dt.utcnow()  # pyright: ignore
        ):
            return True
        else:
            return (
                self.execution_started <= self.start_execution
            )  # pyright: ignore

    @property
    def is_completed_late(self) -> bool:
        if not self.complete_before:  # pyright: ignore
            return False
        elif (
            not self.completed  # pyright: ignore
            and self.complete_before <= _dt.utcnow()  # pyright: ignore
        ):  # pyright: ignore
            return True
        else:
            return self.complete_before < self.completed  # pyright: ignore
