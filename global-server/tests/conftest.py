import pytest

from colorama import Fore, Back, Style

from src.config import settings
from generation import generate_default_data


@pytest.fixture(scope="session", autouse=True)
async def setup():
    assert settings.MODE == "test"
    print(f"\n{Fore.WHITE}{Back.BLUE} Database generation...{Style.RESET_ALL}")
    await generate_default_data()
    print(f"{Fore.WHITE}{Back.BLUE} done {Style.RESET_ALL}")
