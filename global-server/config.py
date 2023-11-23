import os as _os


def getenv(name: str) -> str:
    value = _os.getenv(name)
    if not value:
        raise OSError(f"{name} environment variable not set")
    return value
