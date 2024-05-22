from typing import Generator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://user:password@db/db"

# for async interaction with db
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,
    #execution_options={"isolation_level": "AUTOCOMMIT"}
)

async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> Generator:
    """Dependency for getting async session"""
    try:
        session: AsyncSession = async_session()
        yield session
    finally:
        await session.close()
