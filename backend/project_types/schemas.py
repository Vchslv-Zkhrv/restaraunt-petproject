from typing import Optional as _Optional, List as _List, Union as _Union, Dict as _Dict
from datetime import datetime as _dt

from pydantic import BaseModel as _Base, Field as _Field

from . import literals as _literals


class _Schema(_Base):

    class Config:

        orm_mode = True
        arbitrary_types_allowed = True


class Actor(_Schema):

    id: int


class DefaultActorCreate(_Schema):

    name: str


class DefaultActor(_Schema):

    id: int
    name: str


class TaskTypeCreate(_Schema):

    name: str


class TaskType(_Schema):

    id: int
    name: str


class TaskTarget(_Schema):

    id: int


class UserCreate(_Schema):

    hashed_password: str = _Field(alias="hashedPassword")
    actor_id: int
    role: _literals.user_roles
    email: str
    phone: _Optional[str]
    telegram: _Optional[int]
    lname: _Optional[str]
    fname: str
    sname: _Optional[str]
    gender: _Optional[bool]
    address: _Optional[str]


class User(_Schema):

    id: int
    hashed_password: str = _Field(alias="hashedPassword")
    actor_id: int
    role: _literals.user_roles
    email: str
    phone: _Optional[str]
    telegram: _Optional[int]
    lname: _Optional[str]
    fname: str
    sname: _Optional[str]
    gender: _Optional[bool]
    address: _Optional[str]
    last_online: _dt = _Field(alias="lastOnline", default=_dt.utcnow())
    created: _dt
    deleted: _Optional[_dt]


class UserDelete(_Schema):

    id: int
    hashed_password: str = _Field(alias="hashedPassword")


class VerificationCreate(_Schema):

    user_id: int
    field_name: str = _Field(alias="fieldName")
    value: _Union[int, str]


class Verfication(_Schema):

    id: int
    user_id: int
    field_name: str = _Field(alias="fieldName")
    value: str


class EmployeePositionCreate(_Schema):

    name: str
    salary: float
    expierence_coefficient: float = _Field(alias="expierenceCoefficient", default=1)


class EmployeePosition(_Schema):

    id: int
    name: str
    salary: float
    expierence_coefficient: float = _Field(alias="expierenceCoefficient", default=1)


class EmployeePositionAccessLevel(_Schema):

    position_id: int = _Field(alias="positionId")
    task_type_id: int = _Field(alias="taskTypeId")
    role: _literals.task_access_roles


class EmployeePositionWithAccessLevels(EmployeePosition):

    access_levels: _Dict[_literals.task_access_roles, _List[TaskType]]


class EmployeeCreate(_Schema):

    user: UserCreate
    hiring_date: _dt = _Field(alias="hiringDate")
    position_id: int = _Field(alias="positionId")


class Employee(_Schema):

    id: int
    user: User
    hiring_date: _dt = _Field(alias="hiringDate")
    position_id: EmployeePosition = _Field(alias="positionId")
    on_shift: bool = _Field(alias="onShift")
    fired_date: _Optional[_dt] = _Field(alias="firedDate")


class CustomerCreate(_Schema):

    user: UserCreate


class Customer(_Schema):

    id: int
    user: User


class MaterialGroupCreate(_Schema):

    name: str
    parent_group_id: _Optional[int] = _Field(alias="parentGroupId")


class MaterialGroup(_Schema):

    id: int
    name: str


class MaterialGroupWithChilds(MaterialGroup):

    childs: _List[MaterialGroup]


class MaterialGroupWithTree(MaterialGroup):

    childs: _List[MaterialGroupWithChilds]


class MaterialGroupWithParentChild(MaterialGroup):

    parent_group_id: _Optional[int] = _Field(alias="parentGroupId")
    child_groups_ids: _Optional[_List[int]] = _Field(alias="childGroupsIds")


class MaterialCreate(_Schema):

    name: str
    unit: _literals.units
    price: float
    best_before: _Optional[_dt] = _Field(alias="bestBefore")
    group_id: int = _Field(alias="groupId")


class Material(_Schema):

    id: int
    name: str
    unit: _literals.units
    price: float
    best_before: _Optional[_dt] = _Field(alias="bestBefore")
    group: MaterialGroupWithParentChild
    created: _dt
    stock_balance: _Optional[float]


class MaterialShort(_Schema):

    id: int
    name: str


class MaterialGroupMaterial(_Schema):

    id: int
    name: str
    unit: _literals.units
    price: float
    best_before: _Optional[_dt] = _Field(alias="bestBefore")
    created: _dt
    stock_balance: _Optional[float]


class MaterialGroupWithMaterials(MaterialGroupWithParentChild):

    materials: _List[MaterialGroupMaterial]


class IngridientMaterial(_Schema):

    material_id: int = _Field(alias="materialId")
    im_ratio: float = _Field(alias="imRatio")


class IngridientMaterialWtihName(_Schema):

    material: MaterialShort
    im_ratio: float = _Field(alias="imRatio")


class IngridientCreate(_Schema):

    name: str
    calories: float
    fats: float
    proteins: float
    carbohidrates: float
    materials: _List[IngridientMaterial]


class Ingridient(_Schema):

    id: int
    name: str
    calories: float
    fats: float
    proteins: float
    carbohidrates: float
    materials: _List[IngridientMaterialWtihName]
    created: _dt


class ProductIngridient(_Schema):

    ingridient_id: int = _Field(alias="ingridientId")
    ip_ratio: float = _Field(alias="ipRatio")


class ProductExtraIngridientCreate(_Schema):

    ingridient_id: int = _Field(alias="ingridient_id")
    count: int = _Field(default=1)


class ProductExtraIngrident(_Schema):

    ingridient: Ingridient
    count: int


class ProductCreate(_Schema):

    name: str
    price: _Optional[float]
    sale: _Optional[float]
    best_before: _Optional[_dt] = _Field(alias="bestBefore")
    status: _literals.product_statuses = _Field(default="inactive")
    own_production: bool = _Field(alias="ownProduction")
    ingridients: _List[ProductIngridient]
    available_extras: _List[ProductExtraIngridientCreate] = _Field(alias="availableExtras")


class Product(_Schema):

    id: int
    name: str
    price: _Optional[float]
    sale: _Optional[float]
    best_before: _Optional[_dt] = _Field(alias="bestBefore")
    status: _literals.product_statuses = _Field(default="inactive")
    own_production: bool = _Field(alias="ownProduction")
    ingridients: _List[ProductIngridient]
