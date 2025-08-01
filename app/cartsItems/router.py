# STDLIB
from typing import List

# THIRDPARTY
from fastapi import APIRouter, Depends, HTTPException
from starlette import status

# FIRSTPARTY
from app.carts.dependencies import get_users_cart
from app.carts.models import Carts
from app.cartsItems.dao import CartsItemsDAO
from app.cartsItems.schemas import (
    SAddCartItem,
    SCartsItem,
    SUpdateCartItemQuantity,
)
from app.database import DbSession
from app.exceptions import (
    NotCartsItemException,
    NotProductsException,
    NotTrueProductsQuantityException,
)
from app.products.dao import ProductsDAO

router = APIRouter(
    prefix="/cartsitems",
    tags=["Товары в корзине"],
)


@router.post("/add")
async def add_cart_item(
    session: DbSession,
    cart_item_data: SAddCartItem = Depends(),
    cart: Carts = Depends(get_users_cart),
) -> SCartsItem:
    """
    Создаёт новый товар в корзине.

    Args:
        session: DbSession(AsyncSession) - Асинхронная сессия базы данных.
        cart_item_data: Pydantic модель SAddCartItem, содержащая данные для добавления нового товара в корзину.
        cart: Экземпляр модели Carts, представляющий текущую корзину пользователя,
        полученный через зависимость get_users_cart().

    Returns:
        cart_item: Экземпляр модели CartsItems, представляющий созданный товар в корзине.
    """
    product = await ProductsDAO.find_one_or_none(
        session, id=cart_item_data.product_id, status="ACTIVE"
    )
    if not product:
        raise NotProductsException

    if (
        cart_item_data.quantity < product.min_quantity
        or cart_item_data.quantity > product.max_quantity
    ):
        raise NotTrueProductsQuantityException

    cart_item_search = await CartsItemsDAO.find_one_or_none(
        session, product_id=cart_item_data.product_id, cart_id=cart.id
    )
    if cart_item_search:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cart item already exist by id: {cart_item_search.id}",
        )
    cart_item = await CartsItemsDAO.add_cart_item(
        session,
        cart_id=cart.id,
        product_id=cart_item_data.product_id,
        quantity=cart_item_data.quantity,
    )

    return cart_item


@router.get("/")
async def get_all_cart_items(
    session: DbSession, cart: Carts = Depends(get_users_cart)
) -> List[SCartsItem]:
    """
    Отдаёт все товары в корзине из текущей корзины пользователя.

    Args:
        session: DbSession(AsyncSession) - Асинхронная сессия базы данных.
        cart: Экземпляр модели Carts, представляющий текущую корзину пользователя,
        полученный через зависимость get_users_cart().

    Returns:
        cart_items: Список экземпляров модели CartsItems, представляющий все товары в корзине в текущей корзины пользователя.
    """
    cart_items = await CartsItemsDAO.find_all(session, cart_id=cart.id)

    return cart_items


@router.get("/{cart_item_id}")
async def get_cart_item_by_id(
    session: DbSession, cart_item_id: int, cart: Carts = Depends(get_users_cart)
) -> SCartsItem:
    """
    Отдаёт товар из корзины по ID.

    Args:
        session: DbSession(AsyncSession) - Асинхронная сессия базы данных.
        cart_item_id: ID товара в корзине, который должен быть получен.
        cart: Экземпляр модели Carts, представляющий текущую корзину пользователя,
        полученный через зависимость get_users_cart().

    Returns:
        cart_item: Экземпляр модели CartsItems, представляющий товар в корзине с указанным ID.
    """
    cart_item = await CartsItemsDAO.find_one_or_none(
        session, id=cart_item_id, cart_id=cart.id
    )
    if not cart_item:
        raise NotCartsItemException

    return cart_item


@router.patch("/update")
async def update_carts_items_quantity(
    session: DbSession,
    update_cart_item_q_data: SUpdateCartItemQuantity = Depends(),
    cart: Carts = Depends(get_users_cart),
) -> SCartsItem:
    """
    Изменяет количество товара в корзине.

    Args:
        session: DbSession(AsyncSession) - Асинхронная сессия базы данных.
        update_cart_item_q_data: Pydantic модель SUpdateCartItemQuantity, содержащая данные для изменения количества товара в корзине.
        cart: Экземпляр модели Carts, представляющий текущую корзину пользователя,
        полученный через зависимость get_users_cart().

    Returns:
        cart_item: Экземпляр модели CartsItems, представляющий товар в корзине с изменённым количеством.
    """
    cart_item = await CartsItemsDAO.find_one_or_none(
        session, id=update_cart_item_q_data.cart_item_id, cart_id=cart.id
    )
    if not cart_item:
        raise NotCartsItemException

    product = await ProductsDAO.find_by_id(session, cart_item.product_id)

    if update_cart_item_q_data.action == "reduce":
        if cart_item.quantity - update_cart_item_q_data.quantity < product.min_quantity:  # pyright: ignore [reportOptionalMemberAccess]
            raise NotTrueProductsQuantityException

    if update_cart_item_q_data.action == "increase":
        if cart_item.quantity + update_cart_item_q_data.quantity > product.max_quantity:  # pyright: ignore [reportOptionalMemberAccess]
            raise NotTrueProductsQuantityException

    updated_cart_item = await CartsItemsDAO.update_carts_item(
        session,
        cart_item_id=update_cart_item_q_data.cart_item_id,
        action=update_cart_item_q_data.action,
        quantity=update_cart_item_q_data.quantity,
    )
    return updated_cart_item


@router.delete("/delete/{carts_item_id}")
async def delete_carts_item(
    session: DbSession, carts_item_id: int, cart: Carts = Depends(get_users_cart)
):
    """
    Удаляет товар из корзины.

    Args:
        session: DbSession(AsyncSession) - Асинхронная сессия базы данных.
        carts_item_id: ID товара в корзине, который должен быть удалён.
        cart: Экземпляр модели Carts, представляющий текущую корзину пользователя,
        полученный через зависимость get_users_cart().

    Returns:
        None
    """
    cart_item = await CartsItemsDAO.find_one_or_none(
        session, id=carts_item_id, cart_id=cart.id
    )
    if not cart_item:
        raise NotCartsItemException
    await CartsItemsDAO.delete_carts_item(session, cart_item_id=carts_item_id)
