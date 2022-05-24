from sqlalchemy.ext.asyncio import (
    create_async_engine, AsyncSession
)
from sqlalchemy.orm import sessionmaker

from .cfg import config

async_engine = create_async_engine(config.db_dsn, echo=config.debug, future=True)
async_session = sessionmaker(async_engine, class_=AsyncSession,
                             expire_on_commit=False, autocommit=False)


async def get_session():
    async with async_session() as session:
        yield session
