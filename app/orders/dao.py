# STDLIB
from datetime import date, time
import math
from typing import Literal, Optional

# THIRDPARTY
from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import Field
from sqlalchemy import insert, select
from sqlalchemy.exc import SQLAlchemyError

# FIRSTPARTY
from app.carts.models import Carts
from app.dao.base import BaseDao
from app.database import async_session_maker
from app.logger import logger
from app.orders.models import Orders


class OrdersStatusFilter(Filter):
    status__in: Optional[
        list[Literal["WAITING", "PREPARING", "READY", "DELIVERY", "COMPLETED"]]
    ] = Field(
        default=None,
    )

    class Constants(Filter.Constants):
        model = Orders


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
        try:
            async with async_session_maker() as session:
                total_price = (
                    select(Carts.total_price)
                    .select_from(Carts)
                    .where(Carts.id == cart_id)
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

        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exception"
            else:
                msg = "Unknown Error"

            msg += ": Can not add order"
            extra = {
                "user_id": user_id,
                "cart_id": cart_id,
                "address": address,
                "date_receiving": date_receiving,
                "time_receiving": time_receiving,
                "receiving_method": receiving_method,
                "payment": payment,
                "comment": comment,
            }

            logger.error(msg, extra=extra, exc_info=True)

    @classmethod
    async def find_all_users_orders(  # pyright: ignore [reportIncompatibleMethodOverride]
        cls,
        page: int,
        page_size: int,
        orders_status_filter: OrdersStatusFilter,
    ):
        try:
            async with async_session_maker() as session:
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

        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exception"
            else:
                msg = "Unknown Error"

            msg += ": Can not find all orders"
            extra = {
                "page": page,
                "page_size": page_size,
                "orders_status_filter": orders_status_filter,
            }

            logger.error(msg, extra=extra, exc_info=True)
