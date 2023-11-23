import sys as _sys

import database as _db
from colorama import Fore as _Fore
from colorama import Style as _Style


def get_db_session():
    """
    creates db session, yields it and closes after use
    """
    db = _db.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def clean_database():
    _db.Base.metadata.drop_all(bind=_db.engine)
    _db.Base.metadata.create_all(bind=_db.engine)


if __name__ == "__main__":
    if "--clean" in _sys.argv:
        print(f"{_Fore.RED}Database will be cleared{_Style.RESET_ALL}")
        if input("Are you sure? (y/n) ").lower() == "y":
            clean_database()
