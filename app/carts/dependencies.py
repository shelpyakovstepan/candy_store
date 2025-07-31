# THIRDPARTY
from fastapi import Depends

# FIRSTPARTY
from app.carts.dao import CartsDAO
from app.database import DbSession
from app.users.dependencies import get_current_user
from app.users.models import Users


async def get_users_cart(session: DbSession, user: Users = Depends(get_current_user)):
    cart = await CartsDAO.find_one_or_none(session, user_id=user.id, status="ACTIVE")
    if not cart:
        cart = await CartsDAO.add(session, user_id=user.id)
    return cart
