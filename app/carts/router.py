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
    """
    Отдаёт текущую корзину пользователя.

    Args:
        cart: Экземпляр модели Carts, представляющий текущую корзину пользователя,
        полученный через зависимость get_users_cart().

    Returns:
        cart: Экземпляр модели Carts, представляющий текущую корзину пользователя.
    """
    return cart
