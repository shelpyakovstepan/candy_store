# STDLIB
from typing import Annotated, AsyncGenerator

# THIRDPARTY
from fastapi import Depends
from sqlalchemy import NullPool, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# FIRSTPARTY
from app.config import get_db_url
from app.logger import logger

DATABASE_URL = get_db_url()

engine = create_async_engine(DATABASE_URL, poolclass=NullPool)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
        finally:
            await session.close()


SessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

DbSession = Annotated[AsyncSession, Depends(get_session)]


async def check_db_connection():
    async with SessionLocal() as session:
        try:
            await session.execute(text("SELECT 1"))
            logger.info("Database connection successful")
        except Exception as e:
            logger.error(f"Unsuccessful connection to database: {e}", exc_info=True)
            raise e


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)
