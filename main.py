import asyncio
import logging

from sqlalchemy.ext.asyncio import create_async_engine
from config.config import DATABASE_URL
from database.base import Base
from database.models import *
from collector.listener import listen_new_blocks
from aiogram import Bot
from config.config import BOT_TOKEN
from telegram.bot import dp

async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=BOT_TOKEN)

    await asyncio.gather(
        dp.start_polling(bot),
        listen_new_blocks(bot)
    )

if __name__ == "__main__":
    asyncio.run(main())


# async def create_tables():
#     engine = create_async_engine(DATABASE_URL)
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     print("Таблица успешно создана")
#     await engine.dispose()
#
# if __name__ == "__main__":
#     asyncio.run(create_tables())


