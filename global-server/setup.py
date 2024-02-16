import asyncio
import sys

import database


if __name__ == "__main__":
    if "--init-models" in sys.argv:
        if "y" in input("Database will be cleared. Are you shure? (y/n): ").lower():
            asyncio.run(database.endpoints.init_models())
