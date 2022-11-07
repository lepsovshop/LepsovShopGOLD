# - *- coding: utf- 8 - *-
import asyncio

from aiogram import executor

import filters
import middlewares
from handlers import dp
from utils.db_api.sqlite import create_bdx
from utils.other_func import update_last_profit, update_profit
from utils.set_bot_commands import set_default_commands


async def on_startup(dp):
    filters.setup(dp)
    middlewares.setup(dp)

    await set_default_commands(dp)

    asyncio.create_task(update_last_profit())
    print("~~~~~ Bot was started ~~~~~")


if __name__ == "__main__":
    create_bdx()
    update_profit()

    executor.start_polling(dp, on_startup=on_startup)
