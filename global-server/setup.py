import sys
import asyncio

from src.database.types_.exceptions import GenerationPermitedError
from src.config import settings
from generation import generate_default_data


if "--generate" in sys.argv:
    if settings.MODE == "production":
        raise GenerationPermitedError
    else:
        asyncio.run(generate_default_data())
