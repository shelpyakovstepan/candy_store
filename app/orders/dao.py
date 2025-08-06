# STDLIB
from datetime import date, time
import math

# THIRDPARTY
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

# FIRSTPARTY
from app.carts.models import Carts
from app.dao.base import BaseDao
from app.orders.models import Orders
from app.orders.schemas import OrdersStatusFilter


class OrdersDAO(BaseDao):
    model = Orders

    @classmethod
    async def add_order(
        cls,
        session: AsyncSession,
        user_id: int,
        cart_id: int,
        address: int,
        date_receiving: date,
        time_receiving: time,
        receiving_method: str,
        comment: str,
    ):
        total_price = (
            select(Carts.total_price).select_from(Carts).where(Carts.id == cart_id)
        )
        total_price = await session.execute(total_price)
        total_price = total_price.scalar()

        new_order_query = (
            insert(Orders)
            .values(
                user_id=user_id,
                cart_id=cart_id,
                address=address,
                date_receiving=date_receiving,
                time_receiving=time_receiving,
                receiving_method=receiving_method,
                payment="NONCASH",
                total_price=total_price,
                comment=comment,
                status="WAITING",
            )
            .returning(Orders)
        )

        new_order = await session.execute(new_order_query)
        new_order = new_order.scalar()

        return new_order

    @classmethod
    async def find_all_users_orders(
        cls,
        session: AsyncSession,
        page: int,
        page_size: int,
        orders_status_filter: OrdersStatusFilter,
    ):
        offset = (page - 1) * page_size
        query_filter = orders_status_filter.filter(select(Orders))
        filtered_data = await session.execute(
            query_filter.offset(offset).limit(page_size)
        )
        filtered_data = filtered_data.scalars().all()

        filtered_data = filtered_data + [  # pyright: ignore [reportOperatorIssue]
            {
                "page": page,
                "size": page_size,
                "total": math.ceil(len(filtered_data) / page_size),
            }
        ]

        return filtered_data
