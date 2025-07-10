# THIRDPARTY
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

async_session_maker = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def check_db_connection():
    try:
        async with AsyncSession(engine) as session:
            await session.execute(text("SELECT 1"))
            logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Unsuccessful connection to database: {e}", exc_info=True)
        raise e


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)
