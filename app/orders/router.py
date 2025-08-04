# STDLIB
from datetime import datetime
from typing import List

# THIRDPARTY
from fastapi import APIRouter, Depends
import pytz

# FIRSTPARTY
from app.addresses.dao import AddressesDAO
from app.addresses.dependencies import get_users_address
from app.addresses.schemas import SAddresses
from app.carts.dao import CartsDAO
from app.carts.dependencies import get_users_cart
from app.carts.models import Carts
from app.database import DbSession
from app.exceptions import (
    NotTrueTimeException,
    YouCanNotAddNewOrderException,
    YouCanNotOrderByThisId,
    YouCanNotPayOrderException,
    YouDoNotHaveCartItemsException,
    YouDoNotHaveOrdersException,
    YouDoNotHavePhoneNumberException,
)
from app.logger import logger
from app.orders.dao import OrdersDAO
from app.orders.models import StatusEnum
from app.orders.schemas import SCreateOrder, SOrders
from app.purchases.dao import PurchasesDAO
from app.purchases.utils import generate_payment_link
from app.rabbitmq.base import send_message
from app.rabbitmq.messages_templates import user_orders_text
from app.users.dependencies import get_current_user
from app.users.models import Users

router = APIRouter(
    prefix="/orders",
    tags=["Заказы"],
)


@router.post("/add")
async def create_order(
    session: DbSession,
    order_data: SCreateOrder = Depends(),
    user: Users = Depends(get_current_user),
    cart: Carts = Depends(get_users_cart),
    address: SAddresses = Depends(get_users_address),  # pyright: ignore [reportRedeclaration]
) -> SOrders:
    """
    Создаёт новый заказ и отправляет уведомление пользователю.

    Args:
        session: DbSession(AsyncSession) - Асинхронная сессия базы данных.
        order_data: Pydantic модель SCreateOrder, содержащая данные для добавления нового заказа.
        user: Экземпляр модели Users, представляющий текущего пользователя, полученный через зависимость get_current_user().
        cart: Экземпляр модели Carts, представляющий текущую корзину пользователя,
        полученный через зависимость get_users_cart().
        address: Экземпляр модели Addresses, представляющий текущий адрес пользователя,
        полученный через зависимость get_users_address().

    Returns:
        new_order: Экземпляр модели Orders, представляющий созданный заказ.
    """
    delta = (
        order_data.date_receiving - datetime.now(pytz.timezone("Europe/Moscow")).date()
    )
    if delta.days < 3:
        raise NotTrueTimeException

    if cart.total_price == 0:
        raise YouDoNotHaveCartItemsException

    if order_data.receiving_method == "DELIVERY" and user.phone_number is None:
        raise YouDoNotHavePhoneNumberException

    check_order = await OrdersDAO.find_one_or_none(
        session, user_id=user.id, status="WAITING"
    )
    if check_order:
        raise YouCanNotAddNewOrderException

    new_order = await OrdersDAO.add_order(
        session,
        user_id=user.id,
        cart_id=cart.id,
        address=address.id,
        date_receiving=order_data.date_receiving,
        time_receiving=order_data.time_receiving,
        receiving_method=order_data.receiving_method,
        comment=order_data.comment,  # pyright: ignore [reportArgumentType]
    )

    await AddressesDAO.update(session, address.id, status=False)
    await CartsDAO.update(session, cart.id, status="INACTIVE")
    await send_message(
        {
            "chat_id": user.user_chat_id,
            "text": await user_orders_text(session, order=new_order),  # pyright: ignore [reportArgumentType]
        },
        "messages-queue",
    )
    logger.info("Сообщение о заказе отправлено пользователю в телеграм")
    return new_order


@router.get("/pay")
async def get_payment_link_for_the_order(
    session: DbSession,
    order_id: int,
    user: Users = Depends(get_current_user),
):
    """
    Даёт ссылку пользователю на оплату заказа.

    Args:
        session: DbSession(AsyncSession) - Асинхронная сессия базы данных.
        order_id: ID заказа, который должен быть оплачен.
        user: Экземпляр модели Users, представляющий текущего пользователя, полученный через зависимость get_current_user().

    Returns:
        payment_link: Ссылка на оплату через Robokassa.
    """
    pay_order = await OrdersDAO.find_one_or_none(session, id=order_id, user_id=user.id)
    if not pay_order:
        raise YouDoNotHaveOrdersException

    if pay_order.status != StatusEnum.WAITING:
        raise YouCanNotPayOrderException

    pay_id = await PurchasesDAO.get_next_id(session=session)
    description = f"Оплата за заказ: ({pay_order.total_price}₽)"
    payment_link = generate_payment_link(
        cost=float(pay_order.total_price),
        number=pay_id,
        description=description,
        user_id=pay_order.user_id,
        user_telegram_id=user.user_chat_id,
        order_id=pay_order.id,
    )

    return payment_link


@router.get("/")
async def get_all_orders(
    session: DbSession,
    user: Users = Depends(get_current_user),
) -> List[SOrders]:
    """
    Отдаёт все заказы пользователя.

    Args:
        session: DbSession(AsyncSession) - Асинхронная сессия базы данных.
        user: Экземпляр модели Users, представляющий текущего пользователя, полученный через зависимость get_current_user().

    Returns:
        orders: Список экземпляров модели Orders, представляющий все заказы пользователя.
    """
    orders = await OrdersDAO.find_all(session, user_id=user.id)
    if not orders:
        raise YouDoNotHaveOrdersException

    return orders


@router.get("/{order_id}")
async def get_order_by_id(
    session: DbSession, order_id: int, user: Users = Depends(get_current_user)
) -> SOrders:
    """
    Отдаёт заказ по ID.

    Args:
        session: DbSession(AsyncSession) - Асинхронная сессия базы данных.
        order_id: ID заказа, который должен быть получен.
        user: Экземпляр модели Users, представляющий текущего пользователя, полученный через зависимость get_current_user().

    Returns:
        order: Экземпляр модели Orders, представляющий заказ с указанным ID.
    """
    order = await OrdersDAO.find_one_or_none(session, id=order_id, user_id=user.id)
    if not order:
        raise YouDoNotHaveOrdersException

    return order


@router.delete("/delete/{order_id}")
async def delete_order(
    session: DbSession,
    order_id: int,
    user: Users = Depends(get_current_user),
):
    """
    Удаляет существующий заказ.

    Args:
        session: DbSession(AsyncSession) - Асинхронная сессия базы данных.
        order_id: ID заказа, который должен быть удалён.
        user: Экземпляр модели Users, представляющий текущего пользователя, полученный через зависимость get_current_user().

    Returns:
        None
    """
    check_order = await OrdersDAO.find_one_or_none(
        session, id=order_id, user_id=user.id, status="WAITING"
    )
    if not check_order:
        raise YouCanNotOrderByThisId

    await OrdersDAO.delete(session, id=order_id)
