import asyncio as _asyncio

import config as _config
from aiogram import Bot as _Bot
from aiogram import Dispatcher as _Dp
from aiogram import types as _tg_types
from aiogram.filters.command import Command as _Command
from loguru import logger as _logger


_logger.remove(0)
_logger.add("./logs/tgbot/debug.log", rotation="1MB")


bot = _Bot(token=_config.getenv("TG_TOKEN"))
dp = _Dp()


@dp.message(_Command("start"))
async def on_start(message: _tg_types.Message):
    await message.answer(text="bot started")  # replace later!


@dp.message(_Command("chatid"))
async def get_chat_id(message: _tg_types.Message):
    await message.answer(text=str(message.chat.id))


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    _asyncio.run(main())
