# STDLIB
from typing import List, Literal

# THIRDPARTY
from fastapi import APIRouter, Depends, Query
from fastapi_filter import FilterDepends

# FIRSTPARTY
from app.admin.dependencies import check_admin_status
from app.carts.dao import CartsDAO
from app.cartsItems.dao import CartsItemsDAO
from app.database import DbSession
from app.exceptions import (
    NotOrdersException,
    NotProductsException,
    NotUserException,
    ProductAlreadyExistsException,
)
from app.favourites.dao import FavouritesDAO
from app.logger import logger
from app.orders.dao import OrdersDAO, OrdersStatusFilter
from app.orders.schemas import SOrders
from app.products.dao import ProductsDAO
from app.products.schemas import SProducts, SUpdateProduct
from app.rabbitmq.base import send_message
from app.rabbitmq.messages_templates import update_user_orders_text
from app.users.dao import UsersDAO
from app.users.schemas import SUsers

router = APIRouter(
    prefix="/admins",
    tags=["Для админов"],
    dependencies=[Depends(check_admin_status)],
)


@router.post("/product")
async def add_product(
    session: DbSession,
    name: str,
    category: Literal["Торты", "Пряники"],
    ingredients: List[str],
    unit: Literal["PIECES", "KILOGRAMS"],
    price: int,
    min_quantity: int,
    max_quantity: int,
    description: str,
    image_id: int,
) -> SProducts:
    product = await ProductsDAO.find_one_or_none(session, name=name, category=category)
    if product:
        raise ProductAlreadyExistsException

    product = await ProductsDAO.add(
        session,
        name=name,
        category=category,
        ingredients=ingredients,
        unit=unit,
        price=price,
        min_quantity=min_quantity,
        max_quantity=max_quantity,
        description=description,
        image_id=image_id,
    )

    logger.info("Продукт успешно добавлен")
    return product  # pyright: ignore [reportReturnType]


@router.patch("/product/{product_id}")
async def update_product(
    session: DbSession,
    product_id: int,
    updated_product_data: SUpdateProduct = Depends(),
):
    stored_product = await ProductsDAO.find_by_id(session, product_id)
    if not stored_product:
        raise NotProductsException

    updated_product = await ProductsDAO.update_product(
        session, product_id, updated_product_data
    )

    logger.info("Продукт успешно изменён")
    return updated_product  # pyright: ignore [reportReturnType]


@router.patch("/")
async def change_product_status(
    session: DbSession, product_id: int, status: Literal["ACTIVE", "INACTIVE"]
):
    stored_product = await ProductsDAO.find_by_id(session, product_id)
    if not stored_product:
        raise NotProductsException

    if status == "INACTIVE":
        all_active_carts = await CartsDAO.find_all(session, status="ACTIVE")
        if all_active_carts:
            for active_cart in all_active_carts:
                await CartsItemsDAO.delete(
                    session, product_id=product_id, cart_id=active_cart.id
                )
        await FavouritesDAO.delete(session, product_id=product_id)

    updated_product = await ProductsDAO.update(session, product_id, status=status)
    logger.info("Статус продукта успешно изменён")
    return updated_product


@router.get("/orders")
async def get_all_users_orders(
    session: DbSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(5, le=10, ge=5),
    orders_status_filter: OrdersStatusFilter = FilterDepends(OrdersStatusFilter),
):
    orders = await OrdersDAO.find_all_users_orders(
        session,
        page=page,
        page_size=page_size,
        orders_status_filter=orders_status_filter,
    )

    if not orders:
        raise NotOrdersException

    return orders


@router.patch("/update/{order_id}")
async def change_order_status(
    session: DbSession, order_id: int, status: Literal["READY", "DELIVERY", "COMPLETED"]
) -> SOrders:
    order = await OrdersDAO.find_by_id(session, order_id)
    if not order:
        raise NotOrdersException

    user = await UsersDAO.find_by_id(session, order.user_id)

    updated_order = await OrdersDAO.update(session, order_id, status=status)
    await send_message(
        {
            "chat_id": user.user_chat_id,  # pyright: ignore [reportOptionalMemberAccess]
            "text": await update_user_orders_text(order=updated_order),  # pyright: ignore [reportArgumentType]
        },
        "messages-queue",
    )
    return order


@router.patch("//")
async def change_admin_status(
    session: DbSession, user_id: int, admin_status: bool
) -> SUsers:
    """Изменяет статус админа пользователя."""
    user = await UsersDAO.update(session, user_id, is_admin=admin_status)
    if not user:
        raise NotUserException

    return user  # pyright: ignore [reportReturnType]
