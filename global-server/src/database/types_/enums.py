from enum import Enum as _Enum


class Weekday(_Enum):

    """
    type hint for sqlalchemy models
    """

    sunday = 0
    monday = 1
    tuesday = 2
    wednesday = 3
    thursday = 4
    friday = 5
    saturday = 6


class AccessRole(_Enum):

    """
    Reasons to access task
    """

    read = "read"
    create = "create"
    edit = "edit"
    execute = "execute"
    inspect = "inpect"
    delete = "delete"


class ProductStatus(_Enum):
    active = "active"
    seasonal_active = "seasonal_active"
    seasonal_inactive = "seasonal_inactive"
    inactive = "inactive"
    deleted = "deleted"
    out_of_stock = "out_of_stock"


class RestarauntExternalDepartmentType(_Enum):
    hall = "hall"
    drive_thru = "drive_thru"
    pickup = "pickup"
    delivery = "delivery"


class ItemUnit(_Enum):
    kg = "kg"
    pcs = "pcs"
    liter = "l"


class VerificationFieldName(_Enum):
    email = "email"
    phone = "phone"
    telegram = "telegram"
    address = "address"


class DiscountType(_Enum):
    seasonal = "seasonal"
    combo = "combo"
    promocode = "promocode"
    nth_for_free = "nth_for_free"
    subscription = "subscription"
    personal = "personal"
    bonuses = "bonuses"


class UserRole(_Enum):
    customer = "customer"
    restaurant_employee = "restaurant_employee"
    managment_employee = "managment_employee"
    admin = "admin"


class ItemType(_Enum):
    tare = "tare"
    material = "material"
    inventory = "inventory"


class TaskStatus(_Enum):
    created = "created"
    execution_started = "execution_started"
    complited = "complited"
    rejected = "rejected"
    failed = "failed"
    inspected = "inspected"
    executed = "executed"
