# THIRDPARTY
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class BaseDao:
    model = None

    @classmethod
    async def add(cls, session: AsyncSession, **values):
        query = insert(cls.model).values(**values).returning(cls.model)
        result = await session.execute(query)
        return result.scalar()

    @classmethod
    async def find_by_id(cls, session: AsyncSession, model_id):
        query = select(cls.model).filter_by(id=model_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def find_all(cls, session: AsyncSession, **values):
        query = select(cls.model).filter_by(**values)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def find_one_or_none(cls, session: AsyncSession, **values):
        query = select(cls.model).filter_by(**values)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def delete(cls, session: AsyncSession, **values):
        query = delete(cls.model).filter_by(**values)
        await session.execute(query)

    @classmethod
    async def update(cls, session: AsyncSession, model_id, **values):
        query = (
            update(cls.model)
            .where(cls.model.id == model_id)
            .values(**values)
            .returning(cls.model)
        )
        result = await session.execute(query)

        return result.scalar()


# pyright: reportArgumentType=false
# pyright: reportCallIssue=false
# pyright: reportAttributeAccessIssue=false
