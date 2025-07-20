# STDLIB
from typing import List, Literal

# THIRDPARTY
from fastapi import APIRouter, Depends, Query
from fastapi_filter import FilterDepends

# FIRSTPARTY
from app.admin.dependencies import check_admin_status
from app.cartsItems.dao import CartsItemsDAO
from app.exceptions import (
    NotOrdersException,
    NotProductsException,
    NotUserException,
    ProductAlreadyExistsException,
)
from app.logger import logger
from app.orders.dao import OrdersDAO, OrdersStatusFilter
from app.products.dao import ProductsDAO
from app.products.schemas import SProducts, SUpdateProduct
from app.users.dao import UsersDAO

router = APIRouter(
    prefix="/admin",
    tags=["Для админов"],
    dependencies=[Depends(check_admin_status)],
)


@router.post("/product")
async def add_product(
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
    product = ProductsDAO.find_one_or_none(name=name, category=category)
    if product:
        raise ProductAlreadyExistsException

    product = await ProductsDAO.add(
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
    product_id: int,
    updated_product_data: SUpdateProduct = Depends(),
) -> SProducts:
    stored_product = await ProductsDAO.find_by_id(product_id)
    if not stored_product:
        raise NotProductsException

    updated_product = await ProductsDAO.update_product(product_id, updated_product_data)

    logger.info("Продукт успешно изменён")
    return updated_product  # pyright: ignore [reportReturnType]


@router.delete("/")
async def delete_product(product_id: int):
    stored_product = await ProductsDAO.find_by_id(product_id)
    if not stored_product:
        raise NotProductsException

    await CartsItemsDAO.delete(product_id=product_id)
    await ProductsDAO.delete(id=product_id)
    logger.info("Продукт успешно удалён")


@router.get("/orders")
async def get_all_users_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(5, le=10, ge=5),
    orders_status_filter: OrdersStatusFilter = FilterDepends(OrdersStatusFilter),
):
    orders = await OrdersDAO.find_all_users_orders(
        page=page, page_size=page_size, orders_status_filter=orders_status_filter
    )

    if not orders:
        raise NotOrdersException

    return orders


@router.patch("//")
async def change_admin_status(user_id: int, admin_status: bool):
    """Изменяет статус админа пользователя."""
    user = await UsersDAO.update(user_id, is_admin=admin_status)
    if not user:
        raise NotUserException

    return user  # pyright: ignore [reportReturnType]


# @router.patch("///")
# async def update_cart_total_price(cart_id: int):
#    cart = await CartsDAO.find_one_or_none(id=cart_id)
#    if not cart:
#        raise NotCartException
#    updated_cart = await CartsDAO.update(model_id=cart_id, total_price=0)
#    return updated_cart
