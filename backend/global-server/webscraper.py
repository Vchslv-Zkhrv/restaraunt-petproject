import asyncio as _asyncio

from pydantic import BaseModel as _BM
import aiofiles as _aiofiles
from bs4 import BeautifulSoup as _BS


class Pizza(_BM):

    name: str
    price: int
    ingiridients: str
    img: str


async def parse_dodo_pizzas(raw: str):
    soup = _BS(raw, "html.parser")
    for pizza in soup.find("main").find("section").find_all("article")[2:-3]: # pyright: ignore
        name = pizza.find("main").find("div").text
        ingridients = pizza.find("main").text[len(name):]
        yield Pizza(
            name=name,
            price=int(pizza.find("footer").find("div").text[:-2].split(" ")[-1]),
            ingiridients=ingridients,
            img=(pizza
                 .find("main")
                 .find("picture")
                 .find("source")
                 .get("srcset")
                 .split(",")[-1]
                 .split(" ")[0]
            )
        )


async def main():

    async with _aiofiles.open("../test-data/dodo.html") as dodo:
        raw_dodo = await dodo.read()
        async for pizza in parse_dodo_pizzas(raw_dodo):
            print(pizza.model_dump_json(indent=2), end="\n\n\n\n")


if __name__ == "__main__":
    _asyncio.run(main())

