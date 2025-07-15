# THIRDPARTY
from fastapi import Depends

# FIRSTPARTY
from app.carts.dao import CartsDAO
from app.exceptions import NotCartException
from app.users.dependencies import get_current_user
from app.users.models import Users


async def get_users_cart(user: Users = Depends(get_current_user)):
    cart = await CartsDAO.find_one_or_none(user_id=user.id)
    if not cart:
        raise NotCartException
    return cart
