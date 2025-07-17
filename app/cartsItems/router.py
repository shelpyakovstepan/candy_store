# STDLIB
from typing import Literal

# THIRDPARTY
from fastapi import APIRouter, Depends, HTTPException, Query
from starlette import status

# FIRSTPARTY
from app.carts.dependencies import get_users_cart
from app.carts.models import Carts
from app.cartsItems.dao import CartsItemsDAO
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
    product_id: int, quantity: int = Query(gt=0), cart: Carts = Depends(get_users_cart)
):
    product = await ProductsDAO.find_by_id(product_id)
    if not product:
        raise NotProductsException

    if quantity < product.min_quantity or quantity > product.max_quantity:
        raise NotTrueProductsQuantityException

    cart_item_search = await CartsItemsDAO.find_one_or_none(
        product_id=product_id, cart_id=cart.id
    )
    if cart_item_search:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cart item already exist by id: {cart_item_search.id}",
        )
    cart_item = await CartsItemsDAO.add(
        cart_id=cart.id, product_id=product_id, quantity=quantity
    )

    return cart_item


@router.get("/")
async def get_all_cart_items(cart: Carts = Depends(get_users_cart)):
    cart_items = await CartsItemsDAO.find_all(cart_id=cart.id)

    return cart_items + [{"price": cart.total_price}]  # pyright: ignore [reportOperatorIssue]


@router.patch("/update")
async def update_carts_items_quantity(
    cart_item_id: int,
    action: Literal["reduce", "increase"],
    quantity: int = Query(gt=0),
    cart: Carts = Depends(get_users_cart),
):
    cart_item = await CartsItemsDAO.find_one_or_none(id=cart_item_id, cart_id=cart.id)
    if not cart_item:
        raise NotCartsItemException

    product = await ProductsDAO.find_by_id(cart_item.product_id)

    if action == "reduce":
        if cart_item.quantity - quantity < product.min_quantity:  # pyright: ignore [reportOptionalMemberAccess]
            raise NotTrueProductsQuantityException

    if action == "increase":
        if cart_item.quantity + quantity > product.max_quantity:  # pyright: ignore [reportOptionalMemberAccess]
            raise NotTrueProductsQuantityException

    updated_cart_item = await CartsItemsDAO.update_carts_item(
        cart_item_id=cart_item_id,
        action=action,
        quantity=quantity,
    )
    return updated_cart_item


@router.delete("/delete/{carts_item_id}")
async def delete_carts_item(carts_item_id: int, cart: Carts = Depends(get_users_cart)):
    cart_item = await CartsItemsDAO.find_one_or_none(id=carts_item_id, cart_id=cart.id)
    if not cart_item:
        raise NotCartsItemException
    total_cart_price = await CartsItemsDAO.delete_carts_item(cart_item_id=carts_item_id)
    return total_cart_price
