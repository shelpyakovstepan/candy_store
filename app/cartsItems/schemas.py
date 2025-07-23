# THIRDPARTY
from pydantic import BaseModel


class SCartsItem(BaseModel):
    id: int
    cart_id: int
    product_id: int
    quantity: int
