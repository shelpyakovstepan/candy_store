# STDLIB
from datetime import date, datetime, time
from typing import List, Literal, Optional

# THIRDPARTY
from fastapi import APIRouter, Depends, Query
import pytz

# FIRSTPARTY
from app.addresses.dependencies import get_users_address
from app.addresses.models import Addresses
from app.carts.dao import CartsDAO
from app.carts.dependencies import get_users_cart
from app.carts.models import Carts
from app.exceptions import (
    NotTrueTimeException,
    YouCanNotAddNewOrderException,
    YouCanNotChooseThisPaymentException,
    YouCanNotOrderByThisId,
    YouCanNotPayOrderException,
    YouDoNotHaveCartItemsException,
    YouDoNotHaveOrdersException,
)
from app.logger import logger
from app.orders.dao import OrdersDAO
from app.orders.models import StatusEnum
from app.orders.schemas import SOrders
from app.rabbitmq.base import send_message
from app.rabbitmq.messages_templates import admin_orders_text, user_orders_text
from app.users.dependencies import get_current_user
from app.users.models import Users

router = APIRouter(
    prefix="/orders",
    tags=["Заказы"],
)


@router.post("/add")
async def create_order(
    date_receiving: date,
    time_receiving: time,
    receiving_method: Literal["PICKUP", "DELIVERY"],
    payment: Literal["CASH", "NONCASH"],
    comment: Optional[str] = Query("", max_length=100),
    user: Users = Depends(get_current_user),
    cart: Carts = Depends(get_users_cart),
    address: Addresses = Depends(get_users_address),  # pyright: ignore [reportRedeclaration]
) -> SOrders:
    delta = date_receiving - datetime.now(pytz.timezone("Europe/Moscow")).date()
    if delta.days < 3:
        raise NotTrueTimeException

    if cart.total_price == 0:
        raise YouDoNotHaveCartItemsException

    if receiving_method == "DELIVERY" and payment == "CASH":
        raise YouCanNotChooseThisPaymentException

    check_order = await OrdersDAO.find_one_or_none(
        user_id=user.id, cart_id=cart.id, status="WAITING"
    )
    if check_order:
        raise YouCanNotAddNewOrderException

    new_order = await OrdersDAO.add(
        user_id=user.id,
        cart_id=cart.id,
        address=address.id,
        date_receiving=date_receiving,
        time_receiving=time_receiving,
        receiving_method=receiving_method,
        payment=payment,
        comment=comment,  # pyright: ignore [reportArgumentType]
    )
    await CartsDAO.update(cart.id, status="INACTIVE")
    await send_message(
        {"chat_id": user.user_chat_id, "text": await user_orders_text(order=new_order)},  # pyright: ignore [reportArgumentType]
        "messages-queue",
    )
    logger.info("Сообщение о заказе отправлено пользователю в телеграм")
    return new_order


@router.patch("/pay")
async def pay_for_the_order(
    order_id: int,
) -> SOrders:
    pay_order = await OrdersDAO.find_by_id(order_id)
    if not pay_order:
        raise YouDoNotHaveOrdersException

    if pay_order.status != StatusEnum.WAITING:
        raise YouCanNotPayOrderException

    pay_order = await OrdersDAO.update(order_id, status="PREPARING")
    await send_message(await admin_orders_text(order=pay_order), "admin-queue")  # pyright: ignore [reportArgumentType]

    return pay_order


@router.get("/")
async def get_all_orders(
    user: Users = Depends(get_current_user),
) -> List[SOrders]:
    orders = await OrdersDAO.find_all(user_id=user.id)
    if not orders:
        raise YouDoNotHaveOrdersException

    return orders


@router.delete("/{order_id}")
async def delete_order(
    order_id: int,
    user: Users = Depends(get_current_user),
):
    check_order = await OrdersDAO.find_one_or_none(id=order_id, user_id=user.id)
    if not check_order:
        raise YouCanNotOrderByThisId

    await OrdersDAO.delete(id=order_id)
