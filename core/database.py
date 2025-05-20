from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .config import settings

engine = create_async_engine(settings.database_settings.db_url)

async_session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
