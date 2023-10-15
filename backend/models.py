from datetime import datetime as _dt
from typing import Optional as _Opt, List as _List

from sqlalchemy import Integer as _Int, String as _Str, Float as _Float, DateTime as _Dt, \
    Boolean as _Bool, Column as _Column, ForeignKey as _Fk
from sqlalchemy.orm import relationship as _rel, Mapped as _Map 
from sqlalchemy.schema import PrimaryKeyConstraint as _PKConstraint
import passlib.hash as _hash

from database import Base as _Base


class Actor(_Base):

    __tablename__ = "Actor"

    id = _Column(_Int, primary_key=True, index=True)

    created_tasks: _Map[_List["Task"]] = _rel(back_populates="author")
    redacted_tasks: _Map[_List["Task"]] = _rel(back_populates="redactor")
    tasks_to_execute: _Map[_List["Task"]] = _rel(back_populates="executor")
    tasks_to_inspect: _Map[_List["Task"]] = _rel(back_populates="inspector")
    default_actor: _Map[_Opt["DefaultActor"]] = _rel(back_populates="actor")
    user: _Map[_Opt["User"]] = _rel(back_populates="actor")
    kitchen_area: _Map[_Opt["KitchenArea"]] = _rel(back_populates="actor")


class DefaultActor(_Base):

    __tablename__ = "DefaultActor"

    id = _Column(_Int, _Fk("Actor.id"), primary_key=True, index=True)
    name = _Column(_Str, unique=True, index=True)

    actor: _Map["Actor"] = _rel(back_populates="default_actor")


class TaskType(_Base):

    __tablename__ = "TaskType"

    id = _Column(_Int, primary_key=True, index=True)
    name = _Column(_Str, unique=True, index=True)

    access_levels: _Map[_List["EmployeePositionAccessLevel"]] = _rel(back_populates="task_type")


class TaskTarget(_Base):

    __tablename__ = "TaskTarget"

    id = _Column(_Int, primary_key=True, index=True)

    task: _Map["Task"] = _rel(back_populates="target")
    supply: _Map[_Opt["Supply"]] = _rel(back_populates="task_target")
    shift: _Map[_Opt["Shift"]] = _rel(back_populates="task_target")
    salary: _Map[_Opt["Salary"]] = _rel(back_populates="task_target")
    writeoff: _Map[_Opt["WriteOff"]] = _rel(back_populates="task_target")
    customer_order: _Map[_Opt["CustomerOrder"]] = _rel(back_populates="task_target")
    customer_payment: _Map[_Opt["CustomerPayment"]] = _rel(back_populates="task_target")
    kitchen_order: _Map[_Opt["KitchenOrder"]] = _rel(back_populates="task_target")
    supply_payment: _Map[_Opt["SupplyPayment"]] = _rel(back_populates="task_target")


class SubTask(_Base):

    __tablename__ = "SubTask"

    child_id = _Column(_Int, _Fk("Task.id"), primary_key=True)
    parent_id = _Column(_Int, _Fk("Task.id"), primary_key=True)
    priority = _Column(_Int, nullable=False, default=0)

    subtasks: _Map[_List["Task"]] = _rel(back_populates="parent")
    parent: _Map["Task"] = _rel(back_populates="subtasks")

    __table_args__ = (_PKConstraint(child_id, parent_id), {})


class User(_Base):

    __tablename__ = "User"

    id = _Column(_Int, primary_key=True, index=True)
    hashed_password = _Column(_Str, nullable=False)
    actor_id = _Column(_Int, _Fk("Actor.id"), nullable=False, index=True)
    role = _Column(_Str, nullable=False, index=True)
    email = _Column(_Str, unique=True, index=True)
    phone = _Column(_Int, unique=True, index=True)
    lname = _Column(_Str)
    fname = _Column(_Str, nullable=False)
    sname = _Column(_Str)
    gender = _Column(_Bool)
    address = _Column(_Str)
    last_online = _Column(_Dt, nullable=False, default=_dt.utcnow, index=True)
    created = _Column(_Dt, nullable=False, index=True)
    deleted = _Column(_Dt) 

    actor: _Map["Actor"] = _rel(back_populates="user")
    employee: _Map[_Opt["Employee"]] = _rel(back_populates="user")
    customer: _Map[_Opt["Customer"]] = _rel(back_populates="user")
    verifications: _Map[_List["Verification"]] = _rel(back_populates="user")

    def verify_password(self, password: str) -> bool:
        return _hash.bcrypt.verify(password, str(self.hashed_password))


class Verification(_Base):

    __tablename__ = "Verification"

    id = _Column(_Int, primary_key=True, index=True)
    user_id = _Column(_Int, _Fk("User.id"), nullable=False, index=True)
    field_name = _Column(_Str, nullable=False)
    value = _Column(_Str, nullable=False, unique=True)

    user: _Map["User"] = _rel(back_populates="verifications")


class EmployeePosition(_Base):

    __tablename__ = "EmployeePosition"

    id = _Column(_Int, primary_key=True, index=True)
    name = _Column(_Str, unique=True, nullable=False, index=True)
    salary = _Column(_Float, nullable=False)
    expierence_coefficient = _Column(_Float, nullable=False, default=1)

    employees: _Map[_List["Employee"]] = _rel(back_populates="position")
    access_levels: _Map[_List["EmployeePositionAccessLevel"]] = _rel(back_populates="position")


class EmployeePositionAccessLevel(_Base):

    __tablename__ = "EmployeePositionAccessLevel"

    position_id = _Column(_Int, _Fk("EmployeePosition.id"), primary_key=True)
    task_type_id = _Column(_Int, _Fk("TaskType.id"), primary_key=True)
    role = _Column(_Str, nullable=False, index=True)

    position: _Map["EmployeePosition"] = _rel(back_populates="access_levels")
    task_type: _Map["TaskType"] = _rel(back_populates="access_levels")

    __table_args__ = (_PKConstraint(position_id, task_type_id), {})


class Employee(_Base):

    __tablename__ = "Employee"

    id = _Column(_Int, primary_key=True, index=True)
    user_id = _Column(_Int, _Fk("User.id"), nullable=False, unique=True)
    hiring_date = _Column(_Dt, nullable=False)
    fired_date = _Column(_Dt)
    on_shift = _Column(_Bool, nullable=False, index=True)
    position_id = _Column(_Int, _Fk("EmployeePosition.id"), nullable=False, index=True)

    user: _Map["User"] = _rel(back_populates="employee")
    position: _Map["EmployeePosition"] = _rel(back_populates="employees")
    salaries: _Map[_List["Salary"]] = _rel(back_populates="employee")
    deliveryman: _Map[_Opt["Deliveryman"]] = _rel(back_populates="employee")


class Shift(_Base):

    __tablename__ = "Shift"

    id = _Column(_Int, primary_key=True, index=True)
    task_target_id = _Column(_Int, _Fk("TaskTarget.id"), nullable=False, unique=True, index=True)

    task_target: _Map["TaskTarget"] = _rel(back_populates="shift")


class Customer(_Base):

    __tablename__ = "Customer"

    id = _Column(_Int, primary_key=True, index=True)
    user_id = _Column(_Int, _Fk("User.id"), nullable=False, unique=True, index=True)

    user: _Map["User"] = _rel(back_populates="customer")
    favorites: _Map[_List["CustomerFavoriteProduct"]] = _rel(back_populates="customer")
    shopping_cart_products: _Map[_List["CustomerFavoriteProduct"]] = \
        _rel(back_populates="customer")


class Material(_Base):

    __tablename__ = "Material"

    id = _Column(_Int, primary_key=True, index=True)
    name = _Column(_Str, unique=True, nullable=False, index=True)
    unit = _Column(_Str, nullable=False)
    price = _Column(_Float)
    stock_balance = _Column(_Float)
    best_before = _Column(_Dt)
    group_id = _Column(_Int, _Fk("MaterialGroup.id"), nullable=False)

    group: _Map["MaterialGroup"] = _rel(back_populates="materials")
    ingridients: _Map[_List["IngridientMaterial"]] = _rel(back_populates="material")
    supplies: _Map[_List["SupplyMaterial"]] = _rel(back_populates="mateterial")
    allergic_flags: _Map[_List["MaterialAllergicFlag"]] = _rel(back_populates="material")
    kitchen_order: _Map[_List["KitchenOrderMaterial"]] = _rel(back_populates="material")
    writeoffs: _Map[_List["WriteOffMaterial"]] = _rel(back_populates="material")


class MaterialGroup(_Base):

    __tablename__ = "MaterialGroup"

    id = _Column(_Int, primary_key=True, index=True)
    name = _Column(_Str, nullable=False, unique=True, index=True)

    parent_group: _Map[_Opt["MaterialSubGroup"]] = _rel(back_populates="child")
    subgroups: _Map[_List["MaterialSubGroup"]] = _rel(back_populates="parent")


class MaterialSubGroup(_Base):

    __tablename__ = "MaterialSubGroup"

    parent_id = _Column(_Int, _Fk("MaterialGroup.id"), primary_key=True)
    child_id = _Column(_Int, _Fk("MaterialGroup.id"), primary_key=True)

    parent: _Map["MaterialGroup"] = _rel(back_populates="subgroups")
    child: _Map["MaterialGroup"] = _rel(back_populates="parent_group")

    __table_args__ = (_PKConstraint(child_id, parent_id), {})


class Supply(_Base):

    __tablename__ = "Supply"

    id = _Column(_Int, primary_key=True, index=True)
    task_target_id = _Column(_Int, _Fk("TaskTarget.id"), nullable=False, index=True)

    task_target: _Map["TaskTarget"] = _rel(back_populates="supply")
    materials: _Map[_List["SupplyMaterial"]] = _rel(back_populates="supply")
    payment: _Map["SupplyPayment"] = _rel(back_populates="supply")


class SupplyMaterial(_Base):

    __tablename__ = "SupplyMaterial"

    supply_id = _Column(_Int, _Fk("Supply.id"), primary_key=True)
    material_id = _Column(_Int, _Fk("Material.id"), primary_key=True)
    count = _Column(_Float, nullable=False)

    supply: _Map["Supply"] = _rel(back_populates="materials")
    material: _Map["Material"] = _rel(back_populates="supplies")

    __table_args__ = (_PKConstraint(supply_id, material_id), {})


class Ingridient(_Base):

    __tablename__ = "Ingridient"

    id = _Column(_Int, primary_key=True, index=True)
    name = _Column(_Str, unique=True, nullable=False, index=True)
    calories = _Column(_Float, nullable=False)
    fats = _Column(_Float, nullable=False)
    proteins = _Column(_Float, nullable=False)
    carbohidrates = _Column(_Float, nullable=False)

    materials: _Map[_List["IngridientMaterial"]] = _rel(back_populates="ingridient")
    products: _Map[_List["ProductIngridient"]] = _rel(back_populates="ingridient")
    available_to_add_in_products: _Map[_List["ProductAvailableExtraIngridient"]] = \
        _rel(back_populates="ingridient")


class IngridientMaterial(_Base):

    __tablename__ = "IngridientMaterial"

    material_id = _Column(_Int, _Fk("Material.id"), primary_key=True)
    ingridient_id = _Column(_Int, _Fk("Ingridient.id"), primary_key=True)
    im_ratio = _Column(_Float, nullable=False)

    material: _Map["Material"] = _rel(back_populates="ingridients")
    ingridient: _Map["Ingridient"] = _rel(back_populates="materials")

    __table_args__ = (_PKConstraint(ingridient_id, material_id), {})


class Product(_Base):

    __tablename__ = "Product"

    id = _Column(_Int, primary_key=True, index=True)
    name = _Column(_Str, nullable=False, unique=True, index=True)
    price = _Column(_Float)
    sale = _Column(_Float)
    best_before = _Column(_Dt)
    status = _Column(_Str, nullable=False, index=True)
    own_production = _Column(_Bool, nullable=False)

    ingridients: _Map[_List["ProductIngridient"]] = _rel(back_populates="product")
    customers_who_added_to_favorites: _Map[_List["CustomerFavoriteProduct"]] = \
        _rel(back_populates="product")
    customers_who_added_to_shopping_cart: _Map[_List["CustomerShoppingCartProduct"]] = \
        _rel(back_populates="product")
    customer_orders: _Map[_List["CustomerOrderProduct"]] = _rel(back_populates="product")
    available_extra_ingridients: _Map[_List["ProductAvailableExtraIngridient"]] = \
        _rel(back_populates="product")
    product_category: _Map["ProductCategoryProduct"] = _rel(back_populates="product")
    commercial_events: _Map[_List["CommercialEventProduct"]] = _rel(back_populates="product")


class CommercialEvent(_Base):

    __tablename__ = "CommercialEvent"

    id = _Column(_Int, primary_key=True, index=True)
    name = _Column(_Str, unique=True, index=True, nullable=False)
    start = _Column(_Dt, nullable=False)
    end = _Column(_Dt)

    products: _Map[_List["CommercialEventProduct"]] = _rel(back_populates="commercial_event")


class CommercialEventProduct(_Base):

    __tablename__ = "CommercialEventProduct"

    commercial_event_id = _Column(_Int, _Fk("CommercialEvent.id"), primary_key=True)
    product_id = _Column(_Int, _Fk("Product.id"), primary_key=True)
    discount = _Column(_Float)

    commercial_event: _Map["CommercialEvent"] = _rel(back_populates="products")
    product: _Map["Product"] = _rel(back_populates="commercial_events")

    __table_args__ = (_PKConstraint(commercial_event_id, product_id), {})


class ProductIngridient(_Base):

    __tablename__ = "ProductIngridient"

    product_id = _Column(_Int, _Fk("Product.id"), primary_key=True)
    ingridient_id = _Column(_Int, _Fk("Ingridient.id"), primary_key=True)
    ip_ratio = _Column(_Float, nullable=False)
    editable = _Column(_Bool, nullable=False)
    edit_price = _Column(_Float)
    max_change = _Column(_Float)

    product: _Map["Product"] = _rel(back_populates="ingridients")
    ingridient: _Map["Ingridient"] = _rel(back_populates="products")

    __table_args__ = (_PKConstraint(ingridient_id, product_id), {})


class CustomerFavoriteProduct(_Base):

    __tablename__ = "CustomerFavoriteProduct"

    customer_id = _Column(_Int, _Fk("Customer.id"), primary_key=True)
    product_id = _Column(_Int, _Fk("Product.id"), primary_key=True)

    customer: _Map["Customer"] = _rel(back_populates="favorite_products")
    product: _Map["Product"] = _rel(back_populates="cusomers_who_added_to_favorites")

    __table_args__ = (_PKConstraint(customer_id, product_id), {})


class CustomerShoppingCartProduct(_Base):

    __tablename__ = "CustomerShoppingCartProduct"

    customer_id = _Column(_Int, _Fk("Customer.id"), primary_key=True)
    product_id = _Column(_Int, _Fk("Product.id"), primary_key=True)
    count  = _Column(_Int, nullable=False, default=1)

    customer: _Map["Customer"] = _rel(back_populates="shopping_cart_products")
    product: _Map["Product"] = _rel(back_populates="customers_who_added_to_shopping_cart")

    __table_args__ = (_PKConstraint(customer_id, product_id), {})


class CustomerOrder(_Base):

    __tablename__ = "CustomerOrder"

    id = _Column(_Int, primary_key=True, index=True)
    task_target_id = _Column(_Int, _Fk("TaskTarget.id"), nullable=False, unique=False, index=True)
    status = _Column(_Str, nullable=False)

    task_target: _Map["TaskTarget"] = _rel(back_populates="customer_order")
    products: _Map[_List["CustomerOrderProduct"]] = _rel(back_populates="customer_order")
    online_order: _Map[_Opt["OnlineOrder"]] = _rel(back_populates="customer_order")
    waiter_order: _Map[_Opt["WaiterOrder"]] = _rel(back_populates="customer_order")
    payment: _Map["CustomerPayment"]  = _rel(back_populates="order")


class CustomerOrderProduct(_Base):

    __tablename__ = "CustomerOrderProduct"

    id = _Column(_Int, primary_key=True, index=True)
    order_id = _Column(_Int, _Fk("CustomerOrder.id"), nullable=False, index=True)
    product_id = _Column(_Int, _Fk("Product.id"), nullable=False, index=True)
    count = _Column(_Int, nullable=False, default=1)

    customer_order: _Map["CustomerOrder"] = _rel(back_populates="products")
    product: _Map["Product"] = _rel(back_populates="customer_orders")


class OnlineOrder(_Base):

    __tablename__ = "OnlineOrder"

    id = _Column(_Int, primary_key=True, index=True)
    order_id = _Column(_Int, _Fk("CustomerOrder.id"), nullable=False, index=True, unique=True)
    promocode_text = _Column(_Str, _Fk("Promocode.text"), nullable=True)

    customer_order: _Map["CustomerOrder"] = _rel(back_populates="online_order")
    current_deliveryman: _Map[_Opt["Deliveryman"]] = _rel(back_populates="current_order")
    promocode: _Map[_Opt["Promocode"]] = _rel(back_populates="online_orders")


class ProductAvailableExtraIngridient(_Base):

    __tablename__ = "ProductAvailableExtraIngridient"

    product_id = _Column(_Int, _Fk("Product.id"), primary_key=True)
    ingridient_id = _Column(_Int, _Fk("Ingridient.id"), primary_key=True)
    price = _Column(_Float, nullable=False)

    product: _Map["Product"] = _rel(back_populates="available_extra_ingridients")
    ingridient: _Map["Ingridient"] = _rel(back_populates="available_to_add_in_products")

    __table_args__ = (_PKConstraint(ingridient_id, product_id), {})


class CustomerOrderProductIngridientChange(_Base):

    __tablename__ = "CustomerOrderProductIngridientChange"

    order_product_id = _Column(_Int, _Fk("CustomerOrderProduct.id"), primary_key=True)
    ingridient_id = _Column(_Int, _Fk("Ingridient.id"), primary_key=True)
    ip_ratio_change = _Column(_Float, nullable=False)

    order_product: _Map["CustomerOrderProduct"] = _rel(back_populates="changed_ingridients")
    ingridient: _Map["Ingridient"] = _rel(back_populates="changed_in_order_products")

    __table_args__ = (_PKConstraint(ingridient_id, order_product_id), {})


class CustomerOrderProductExtraIngridient(_Base):

    __tablename__ = "CustomerOrderExtraIngridient"

    order_product_id = _Column(_Int, _Fk("CustomerOrderProduct.id"), primary_key=True)
    ingridient_id = _Column(_Int, _Fk("Ingridient.id"), primary_key=True)
    count = _Column(_Int, nullable=False, default=1)

    order_product: _Map["CustomerOrderProduct"] = _rel(back_populates="extra_ingridients")
    ingridient: _Map["Ingridient"] = _rel(back_populates="added_to_order_products")

    __table_args__ = (_PKConstraint(ingridient_id, order_product_id), {})


class Table(_Base):

    __tablename__ = "Table"

    id = _Column(_Int, primary_key=True, index=True)
    number = _Column(_Int, nullable=False, unique=True, index=True)
    location_id = _Column(_Int, _Fk("TableLocation.id"), nullable=False, index=True)

    location: _Map["TableLocation"] = _rel(back_populates="tables")
    waiter_orders: _Map[_List["WaiterOrder"]] = _rel(back_populates="table")


class TableLocation(_Base):

    __tablename__ = "TableLocation"

    id = _Column(_Int, primary_key=True, index=True)
    name = _Column(_Str, unique=True, index=True, nullable=False)

    tables: _Map[_List["Table"]] = _rel(back_populates="location")


class WaiterOrder(_Base):

    __tablename__ = "WaiterOrder"

    id = _Column(_Int, primary_key=True, index=True)
    table_id = _Column(_Int, _Fk("Table.id"), nullable=False)
    order_Id = _Column(_Int, _Fk("CustomerOrder.id"), nullable=False, unique=True, index=True)

    table: _Map["Table"] = _rel(back_populates="waiter_orders")
    customer_order: _Map["CustomerOrder"] = _rel(back_populates="waiter_order")


class Salary(_Base):

    __tablename__ = "Salary"

    id = _Column(_Int, primary_key=True, index=True)
    task_target_id = _Column(_Int, _Fk("TaskTarget.id"), nullable=False, unique=True, index=True)
    employee_id = _Column(_Int, _Fk("Employee.id"), nullable=False, index=True)
    bonus = _Column(_Float)

    task_target: _Map["TaskTarget"] = _rel(back_populates="salary")
    employee: _Map["Employee"] = _rel(back_populates="salaries")


class AllergicFlag(_Base):

    __tablename__ = "AllergicFlag"

    id = _Column(_Int, primary_key=True, index=True)
    name = _Column(_Str, unique=True, index=True, nullable=False)

    materials: _Map[_List["MaterialAllergicFlag"]] = _rel(back_populates="allergic_flag")


class MaterialAllergicFlag(_Base):

    __tablename__ = "MaterialAllergicFlag"

    material_id = _Column(_Int, _Fk("Material.id"), primary_key=True)
    flag_id = _Column(_Int, _Fk("AllergicFlag.id"), primary_key=True)

    material: _Map["Material"] = _rel(back_populates="allergic_flags")
    allergic_flag: _Map["AllergicFlag"] = _rel(back_populates="materials")

    __table_args__ = (_PKConstraint(material_id, flag_id), {})


class ProductCategory(_Base):

    __tablename__ = "ProductCategory"

    id = _Column(_Int, primary_key=True, index=True)
    name = _Column(_Str, unique=True, index=True, nullable=False)

    products: _Map[_List["ProductCategoryProduct"]] = _rel(back_populates="product_category")
    kitchen_area: _Map["KitchenAreaProductCategory"] = _rel(back_populates="product_category")


class ProductCategoryProduct(_Base):

    __tablename__ = "ProductCategoryProduct"

    product_id = _Column(_Int, _Fk("Product.id"), primary_key=True)
    category_id = _Column(_Int, _Fk("ProductCategory.id"), primary_key=True)

    product: _Map["Product"] = _rel(back_populates="product_category")
    product_category: _Map["ProductCategory"] = _rel(back_populates="products")

    __table_args__ = (_PKConstraint(product_id, category_id), {})


class KitchenArea(_Base):

    __tablename__ = "KitchenArea"

    id = _Column(_Int, primary_key=True, index=True)
    actor_id = _Column(_Int, _Fk("Actor.id"), unique=True, index=True, nullable=False)
    name = _Column(_Str, unique=True, nullable=False, index=True)

    actor: _Map["Actor"] = _rel(back_populates="kitchen_area")
    product_categories: _Map[_List["KitchenAreaProductCategory"]] = \
        _rel(back_populates="kitchen_area")


class KitchenAreaProductCategory(_Base):

    __tablename__ = "KitchenAreaProductCategory"

    kitchen_area_id = _Column(_Int, _Fk("KitchenArea.id"), primary_key=True)
    product_category_id = _Column(_Int, _Fk("ProductCategory.id"), primary_key=True)

    kitchen_area: _Map["KitchenArea"] = _rel(back_populates="product_categories")
    product_category: _Map["ProductCategory"] = _rel(back_populates="kitchen_area")

    __table_args__ = (_PKConstraint(kitchen_area_id, product_category_id), {})


class CustomerPayment(_Base):

    __tablename__ = "CustomerPayment"

    id = _Column(_Int, primary_key=True, index=True)
    order_id = _Column(_Int, _Fk("CustomerOrder.id"), unique=True, nullable=False, index=True)
    task_target_id = _Column(_Int, _Fk("TaskTarget.id"), nullable=False, index=True, unique=True)

    order: _Map["CustomerOrder"] = _rel(back_populates="payment")
    task_target: _Map["TaskTarget"] = _rel(back_populates="customer_payment")


class Deliveryman(_Base):

    __tablename__ = "Deliveryman"

    id = _Column(_Int, primary_key=True, index=True)
    employee_id = _Column(_Int, _Fk("Employee.id"), unique=True, index=True, nullable=False)
    geolocation = _Column(_Str)
    current_order_id = _Column(_Int, _Fk("OnlineOrder.id"), unique=True, index=True, nullable=True)

    employee: _Map["Employee"] = _rel(back_populates="deliveryman")
    current_order: _Map["OnlineOrder"] = _rel(back_populates="current_deliveryman")


class Promocode(_Base):

    __tablename__ = "Promocode"

    text = _Column(_Str, primary_key=True, index=True)
    start = _Column(_Dt)
    end = _Column(_Dt)

    online_orders: _Map[_List["OnlineOrder"]] = _rel(back_populates="promocode")


class KitchenOrder(_Base):

    __tablename__ = "KitchenOrder"

    id = _Column(_Int, primary_key=True, index=True)
    task_target_id = _Column(_Int, _Fk("TaskTarget.id"), index=True, nullable=False, unique=True)

    task_target: _Map["TaskTarget"] = _rel(back_populates="kitchen_order")
    material: _Map[_List["KitchenOrderMaterial"]] = _rel(back_populates="kitchen_order")


class KitchenOrderMaterial(_Base):

    __tablename__ = "KitchenOrderMaterial"

    kitchen_order_id = _Column(_Int, _Fk("KitchenOrder.id"), primary_key=True)
    material_id = _Column(_Int, _Fk("Material.id"), primary_key=True)
    count = _Column(_Float, nullable=False)

    kitchen_order: _Map["KitchenOrder"] = _rel(back_populates="materials")
    material: _Map["Material"] = _rel(back_populates="kitchen_orders")

    __table_args__ = (_PKConstraint(kitchen_order_id, material_id), {})


class WriteOffReason(_Base):

    __tablename__ = "WriteOffReason"

    id = _Column(_Int, primary_key=True, index=True)
    name = _Column(_Str, unique=True, nullable=False, index=True)
    descritption = _Column(_Str)

    writeoffs: _Map[_List["WriteOff"]] = _rel(back_populates="reason")


class WriteOff(_Base):

    __tablename__ = "WriteOff"

    id = _Column(_Int, primary_key=True, index=True)
    task_target_id = _Column(_Int, _Fk("TaskTarget.id"), nullable=False, index=True, unique=True)
    reason_id = _Column(_Int, _Fk("WriteOffReason.id"), nullable=False, index=True)

    task_target: _Map["TaskTarget"] = _rel(back_populates="writeoff")
    reason: _Map["WriteOffReason"] =  _rel(back_populates="writeoffs")
    materials: _Map[_List["WriteOffMaterial"]] = _rel(back_populates="writeoff")


class WriteOffMaterial(_Base):

    __tablename__ = "WriteOffMaterial"

    writeoff_id = _Column(_Int, _Fk("WriteOff.id"), primary_key=True)
    material_id = _Column(_Int, _Fk("Material.id"), primary_key=True)
    count = _Column(_Float, nullable=False)

    writeoff: _Map["WriteOff"] = _rel(back_populates="materials")
    material: _Map["Material"] = _rel(back_populates="writeoffs")

    __table_args__ = (_PKConstraint(writeoff_id, material_id), {})


class SupplyPayment(_Base):

    __tablename__ = "SupplyPayment"

    id = _Column(_Int, primary_key=True, index=True)
    task_target_id = _Column(_Int, _Fk("TaskTarget.id"), index=True, unique=True, nullable=False)
    supply_id = _Column(_Int, _Fk("Supply.id"), index=True, unique=True, nullable=False)

    task_target: _Map["TaskTarget"] = _rel(back_populates="supply_payment")
    supply: _Map["Supply"] = _rel(back_populates="payment")


class Task(_Base):

    __tablename__ = "Task"

    id = _Column(_Int, primary_key=True, index=True)
    name = _Column(_Str, nullable=False)
    comment = _Column(_Str)
    status = _Column(_Str, nullable=False, index=True)
    target_id = _Column(_Int, _Fk("TaskTarget.id"), nullable=False, index=True)
    created = _Column(_Dt, nullable=False, default=_dt.utcnow, index=True)
    author_id = _Column(_Int, _Fk("Actor.id"), nullable=False, index=True)
    changed = _Column(_Dt)
    redactor_id = _Column(_Int, _Fk("Actor.id"), nullable=True)
    start_execution = _Column(_Dt, index=True)
    execution_started = _Column(_Dt)
    fail_on_late_start = _Column(_Bool, nullable=False, default=False)
    complete_before = _Column(_Dt)
    completed = _Column(_Dt)
    fail_on_late_complete = _Column(_Bool, nullable=False, default=False)
    executor_id = _Column(_Int, _Fk("Actor.id"), nullable=False, index=True)
    approved = _Column(_Dt, index=True)
    inspector_id = _Column(_Int, _Fk("Actor.id"), nullable=False, index=True)

    tasktype: _Map["TaskType"] = _rel(back_populates="tasks")
    target: _Map["TaskTarget"] = _rel(back_populates="task")
    author: _Map["Actor"] = _rel(back_populates="created_tasks")
    redactor: _Map[_Opt["Actor"]] = _rel(back_populates="redacted_tasks")
    executor: _Map["Actor"] = _rel(back_populates="tasks_to_execute")
    inspector: _Map["Actor"] = _rel(back_populates="tasks_to_inspect")
    parent: _Map[_Opt["SubTask"]] = _rel(back_populates="subtasks")
    subtasks: _Map[_List["SubTask"]] = _rel(back_populates="parent")

    def is_started_late(self) -> bool:
        if not self.start_execution: #pyright: ignore
            return False
        elif not self.execution_started and self.start_execution <= _dt.utcnow(): #pyright: ignore
            return True
        else:
            return self.execution_started <= self.start_execution #pyright: ignore

    def is_completed_late(self) -> bool:
        if not self.complete_before: #pyright: ignore
            return False
        elif not self.completed and self.complete_before <= _dt.utcnow(): #pyright: ignore
            return True
        else:
            return self.complete_before < self.completed #pyright: ignore

