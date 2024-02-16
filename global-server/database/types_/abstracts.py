"""
Abstract classes for sqlalchemy models.

(Classes are not inherited from abc.ABC because of metaclass conflict)
"""


import abc as _abc
import typing as _t

from sqlalchemy import orm as _orm

from . import enums as _enums


class Item:

    """Abstract class for base Item model"""

    id: _orm.Mapped[int]

    @property
    def _impl_and_type(
        self,
    ) -> _t.Tuple["ItemImplementation", _enums.ItemType]:
        for t in _enums.ItemType:
            impl = self.__getattribute__(t.value)
            if impl:
                return impl, t
        else:
            raise TypeError("Item implementation is not specified in ItemType")

    @property
    def implementation(self) -> "ItemImplementation":
        return self._impl_and_type[0]

    @property
    def type_(self) -> _enums.ItemType:
        return self._impl_and_type[1]


class ItemImplementation:

    """Implementation of Item model"""

    id: _orm.Mapped[int]
    item_id: _orm.Mapped[int]
    group_id: _orm.Mapped[int]


class ItemImplementationGroup:

    """Group of ItemImplementation of one type"""

    id: _orm.Mapped[int]
    name: _orm.Mapped[str]


class ItemImplementationCollection:

    """Collection of ItemImplementation of different types"""

    id: _orm.Mapped[int]
    name: _orm.Mapped[str]


class ItemImplementationRelation:

    """ItemImplementation in AbstractItemCollection"""

    item_id: _orm.Mapped[int]

    @property
    @_abc.abstractmethod
    def _collection(self) -> ItemImplementationCollection:
        ...

    @property
    def _collection_id(self) -> int:
        return self._collection.id
