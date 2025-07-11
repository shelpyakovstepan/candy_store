# THIRDPARTY
from sqlalchemy import delete, insert, select, update

# FIRSTPARTY
from app.database import async_session_maker


class BaseDao:
    model = None

    @classmethod
    async def add(cls, **values):
        async with async_session_maker() as session:
            query = insert(cls.model).values(**values).returning(cls.model)
            result = await session.execute(query)
            await session.commit()
            return result.scalar()

    @classmethod
    async def find_by_id(cls, model_id):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(id=model_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def find_all(cls, **values):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**values)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def find_one_or_none(cls, **values):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**values)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def delete(cls, **values):
        async with async_session_maker() as session:
            query = delete(cls.model).filter_by(**values)
            await session.execute(query)
            await session.commit()

    @classmethod
    async def update_one(cls, model_id, **values):
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


# pyright: reportArgumentType=false
# pyright: reportCallIssue=false
# pyright: reportAttributeAccessIssue=false
