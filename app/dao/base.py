# THIRDPARTY
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import SQLAlchemyError

# FIRSTPARTY
from app.database import async_session_maker
from app.logger import logger


class BaseDao:
    model = None

    @classmethod
    async def add(cls, **values):
        try:
            async with async_session_maker() as session:
                query = insert(cls.model).values(**values).returning(cls.model)
                result = await session.execute(query)
                await session.commit()
                return result.scalar()

        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exception"
            else:
                msg = "Unknown Error"
            msg += ": Can not add"

            logger.error(msg, exc_info=True)

    @classmethod
    async def find_by_id(cls, model_id):
        try:
            async with async_session_maker() as session:
                query = select(cls.model).filter_by(id=model_id)
                result = await session.execute(query)
                return result.scalar_one_or_none()

        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exception"
            else:
                msg = "Unknown Error"

            msg += ": Can not find by id"

            logger.error(msg, exc_info=True)

    @classmethod
    async def find_all(cls, **values):
        try:
            async with async_session_maker() as session:
                query = select(cls.model).filter_by(**values)
                result = await session.execute(query)
                return result.scalars().all()

        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exception"
            else:
                msg = "Unknown Error"

            msg += ": Can not find all"

            logger.error(msg, exc_info=True)

    @classmethod
    async def find_one_or_none(cls, **values):
        try:
            async with async_session_maker() as session:
                query = select(cls.model).filter_by(**values)
                result = await session.execute(query)
                return result.scalar_one_or_none()

        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exception"
            else:
                msg = "Unknown Error"

            msg += ": Can not find one or none"

            logger.error(msg, exc_info=True)

    @classmethod
    async def delete(cls, **values):
        try:
            async with async_session_maker() as session:
                query = delete(cls.model).filter_by(**values)
                await session.execute(query)
                await session.commit()

        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exception"
            else:
                msg = "Unknown Error"

            msg += ": Can not delete"

            logger.error(msg, exc_info=True)

    @classmethod
    async def update(cls, model_id, **values):
        try:
            async with async_session_maker() as session:
                query = (
                    update(cls.model)
                    .where(cls.model.id == model_id)
                    .values(**values)
                    .returning(cls.model)
                )
                result = await session.execute(query)
                await session.commit()

                return result.scalar()

        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exception"
            else:
                msg = "Unknown Error"

            msg += ": Can not delete"

            logger.error(msg, exc_info=True)


# pyright: reportArgumentType=false
# pyright: reportCallIssue=false
# pyright: reportAttributeAccessIssue=false
