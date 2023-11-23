from typing import Literal as _Literal


task_access_roles = _Literal["read", "create", "edit", "execute", "inspect", "delete"]

user_roles = _Literal["default_actor", "kitchen_area", "employee", "customer", "root", "admin"]

units = _Literal["kg", "pcs", "l"]

product_statuses = _Literal[
    "active", "seasonal: active", "seasonal: inactive", "inactive", "deleted" "out of stock"
]
