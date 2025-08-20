import asyncio

from sqlalchemy.ext.asyncio import create_async_engine

from config.config import DATABASE_URL
from database.base import Base
from database.models import *

async def create_tables():
    print("Подключение к бд")
    engine = create_async_engine(DATABASE_URL, echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        print("Создаём новые таблицы")
        await conn.run_sync(Base.metadata.create_all)

    print("Таблицы созданы")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_tables())