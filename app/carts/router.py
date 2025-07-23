# THIRDPARTY
from fastapi import APIRouter, Depends

# FIRSTPARTY
from app.carts.dependencies import get_users_cart
from app.carts.models import Carts

router = APIRouter(
    prefix="/carts",
    tags=["Корзина"],
)


@router.get("/")
async def get_cart(cart: Carts = Depends(get_users_cart)):
    return cart
