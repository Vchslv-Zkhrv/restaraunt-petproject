import sys
import asyncio

from database.generation import generate_default_data
from database.types_.exceptions import GenerationPermitedError
import config


if "--generate" in sys.argv:
    if config.env.mode == "production":
        raise GenerationPermitedError
    else:
        asyncio.run(generate_default_data())
