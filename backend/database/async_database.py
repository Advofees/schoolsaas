from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from backend.database.database import DATABASE_URL


AsyncSQLAlchemyEngine = create_async_engine(DATABASE_URL)
AsyncSQLAlchemySessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=AsyncSQLAlchemyEngine
)


def get_async_db():
    return AsyncSession()


async def get_async_db_from_generator():
    db = AsyncSession()
    try:
        yield db
    finally:
        await db.close()


AsyncDatabaseDependency = Annotated[AsyncSession, Depends(get_async_db_from_generator)]