# STDLIB
from datetime import date, time

# THIRDPARTY
from sqlalchemy import insert, select

# FIRSTPARTY
from app.carts.models import Carts
from app.dao.base import BaseDao
from app.database import async_session_maker
from app.orders.models import Orders


class OrdersDAO(BaseDao):
    model = Orders

    @classmethod
    async def add(  # pyright: ignore [reportIncompatibleMethodOverride]
        cls,
        user_id: int,
        cart_id: int,
        address: int,
        date_receiving: date,
        time_receiving: time,
        receiving_method: str,
        payment: str,
        comment: str,
    ):
        async with async_session_maker() as session:
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
                    payment=payment,
                    total_price=total_price,
                    comment=comment,
                    status="WAITING",
                )
                .returning(Orders)
            )

            new_order = await session.execute(new_order_query)
            await session.commit()
            new_order = new_order.scalar()

            return new_order
