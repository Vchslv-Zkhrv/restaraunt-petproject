import sqlalchemy.orm as _orm
from fastapi import security as _security

from . import models as _models
from . import project_types as _types


oauth2schema = _security.OAuth2PasswordBearer(tokenUrl="/api/token")


async def auth(
    id: int, role: _types.literals.user_roles, password: str, db: _orm.Session
) -> _models.User:
    """
    Single authorization method for all users
    """
    user = db.get(_models.User, id)
    if not user:
        raise _types.exceptions.NoSuchUserError
    if user.deleted:  # pyright: ignore
        raise _types.exceptions.DeletedUserAuthError
    if user.role != role:  # pyright: ignore
        raise _types.exceptions.AuthRoleError
    if not user.verify_password(password):
        raise _types.exceptions.PasswordError
    return user
