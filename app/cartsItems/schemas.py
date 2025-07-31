# STDLIB
from typing import Literal

# THIRDPARTY
from fastapi import Query
from pydantic import BaseModel


class SCartsItem(BaseModel):
    id: int
    cart_id: int
    product_id: int
    quantity: int


class SAddCartItem(BaseModel):
    product_id: int
    quantity: int = Query(gt=0)


class SUpdateCartItemQuantity(BaseModel):
    cart_item_id: int
    action: Literal["reduce", "increase"]
    quantity: int = Query(gt=0)
