import datetime as _dt

import sqlalchemy as _sql
import sqlalchemy.orm as _orm
import passlib.hash as _hash

from database import Base as _Base


class Actor(_Base):

    __tablename__ = "Actor"

    id = _sql.Column(_sql.Integer, primary_key=True, index=True)

    default_actor: _orm.Mapped["DefaultActor"] = _orm.relationship(back_populates="actor")


class DefaultActor(_Base):

    __tablename__ = "DefaultActor"

    id = _sql.Column(_sql.Integer, _sql.ForeignKey("Actor.id"), primary_key=True, index=True)
    name = _sql.Column(_sql.String, unique=True, index=True)

    actor: _orm.Mapped["Actor"] = _orm.relationship(back_populates="default_actor")

