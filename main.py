import asyncio

from sqlalchemy.ext.asyncio import create_async_engine
from config.config import DATABASE_URL
from database.base import Base
from database.models import *
from collector.listener import listen_new_blocks


# async def create_tables():
#     engine = create_async_engine(DATABASE_URL)
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     print("Таблица успешно создана")
#     await engine.dispose()
#
# if __name__ == "__main__":
#     asyncio.run(create_tables())

if __name__ == "__main__":
    print("Запускаем сервис сбора данных...")
    asyncio.run(listen_new_blocks())


