from requests import session
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, async_engine_from_config
from contextlib import asynccontextmanager
from config.config import DATABASE_URL

async_engine = create_async_engine(DATABASE_URL)

async_session_factory = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False
)

@asynccontextmanager
async def get_db_session():
    async with async_session_factory() as session:
        yield session

