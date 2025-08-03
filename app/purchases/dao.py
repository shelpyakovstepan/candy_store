# THIRDPARTY
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

# FIRSTPARTY
from app.dao.base import BaseDao
from app.purchases.models import Purchases


class PurchasesDAO(BaseDao):
    model = Purchases

    @classmethod
    async def get_next_id(cls, session: AsyncSession) -> int:
        """
         Возвращает следующий свободный ID для новой записи.

         Args:
             session: DbSession(AsyncSession) - Асинхронная сессия базы данных.

        Returns:
            Следующий свободный ID
        """
        query = select(func.coalesce(func.max(cls.model.id) + 1, 1))
        result = await session.execute(query)
        return result.scalar()
