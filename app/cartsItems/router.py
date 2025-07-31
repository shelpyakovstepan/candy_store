# STDLIB
from typing import List, Literal

# THIRDPARTY
from fastapi import APIRouter, Depends, HTTPException, Query
from starlette import status

# FIRSTPARTY
from app.carts.dependencies import get_users_cart
from app.carts.models import Carts
from app.cartsItems.dao import CartsItemsDAO
from app.cartsItems.schemas import SCartsItem
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
    product_id: int,
    quantity: int = Query(gt=0),
    cart: Carts = Depends(get_users_cart),
) -> SCartsItem:
    product = await ProductsDAO.find_one_or_none(
        session, id=product_id, status="ACTIVE"
    )
    if not product:
        raise NotProductsException

    if quantity < product.min_quantity or quantity > product.max_quantity:
        raise NotTrueProductsQuantityException

    cart_item_search = await CartsItemsDAO.find_one_or_none(
        session, product_id=product_id, cart_id=cart.id
    )
    if cart_item_search:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cart item already exist by id: {cart_item_search.id}",
        )
    cart_item = await CartsItemsDAO.add_cart_item(
        session, cart_id=cart.id, product_id=product_id, quantity=quantity
    )

    return cart_item


@router.get("/")
async def get_all_cart_items(
    session: DbSession, cart: Carts = Depends(get_users_cart)
) -> List[SCartsItem]:
    cart_items = await CartsItemsDAO.find_all(session, cart_id=cart.id)

    return cart_items


@router.patch("/update")
async def update_carts_items_quantity(
    session: DbSession,
    cart_item_id: int,
    action: Literal["reduce", "increase"],
    quantity: int = Query(gt=0),
    cart: Carts = Depends(get_users_cart),
) -> SCartsItem:
    cart_item = await CartsItemsDAO.find_one_or_none(
        session, id=cart_item_id, cart_id=cart.id
    )
    if not cart_item:
        raise NotCartsItemException

    product = await ProductsDAO.find_by_id(session, cart_item.product_id)

    if action == "reduce":
        if cart_item.quantity - quantity < product.min_quantity:  # pyright: ignore [reportOptionalMemberAccess]
            raise NotTrueProductsQuantityException

    if action == "increase":
        if cart_item.quantity + quantity > product.max_quantity:  # pyright: ignore [reportOptionalMemberAccess]
            raise NotTrueProductsQuantityException

    updated_cart_item = await CartsItemsDAO.update_carts_item(
        session,
        cart_item_id=cart_item_id,
        action=action,
        quantity=quantity,
    )
    return updated_cart_item


@router.delete("/delete/{carts_item_id}")
async def delete_carts_item(
    session: DbSession, carts_item_id: int, cart: Carts = Depends(get_users_cart)
):
    cart_item = await CartsItemsDAO.find_one_or_none(
        session, id=carts_item_id, cart_id=cart.id
    )
    if not cart_item:
        raise NotCartsItemException
    total_cart_price = await CartsItemsDAO.delete_carts_item(
        session, cart_item_id=carts_item_id
    )
    return total_cart_price
