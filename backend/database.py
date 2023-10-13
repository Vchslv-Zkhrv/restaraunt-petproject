import sqlalchemy as _sql
import sqlalchemy.orm as _orm

from config import getenv as _env

engine = _sql.create_engine(
    _env("DB_CONNECT_URL")
)


SessionLocal = _orm.sessionmaker(
    bind=engine
)

Base = _orm.declarative_base()


