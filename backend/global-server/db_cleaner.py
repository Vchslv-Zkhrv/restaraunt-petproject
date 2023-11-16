import sys as _sys

from colorama import Fore as _Fore

import models as _models
import database as _db


def clean_database():
    _db.Base.metadata.drop_all(bind=_db.engine)
    _db.Base.metadata.create_all(bind=_db.engine)


def create_default_actors():
    pass

if __name__ == "__main__":

    if "--drop" in _sys.argv:
        print(f"{_Fore.RED}Database will be cleared{_Fore.RESET}")
        if input("Are you sure? (y/n) ").lower() == "y":
            clean_database()

