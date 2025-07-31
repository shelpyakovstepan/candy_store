# THIRDPARTY
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

# FIRSTPARTY
from app.carts.dao import CartsDAO


class TestCartsDAO:
    async def test_carts_add(self, get_session: AsyncSession, create_user):
        cart = await CartsDAO.add(session=get_session, user_id=create_user.id)

        assert cart is not None
        assert cart.user_id == create_user.id

    @pytest.mark.parametrize(
        "user_id, status, exists",
        [
            (222222, "ACTIVE", True),
            (333333, "ACTIVE", False),
        ],
    )
    async def test_carts_find_one_or_none(
        self,
        get_session: AsyncSession,
        create_user,
        create_cart,
        user_id,
        status,
        exists,
    ):
        cart = await CartsDAO.find_one_or_none(
            session=get_session, user_id=user_id, status=status
        )

        if exists:
            assert cart is not None
            assert cart.user_id == user_id
        else:
            assert cart is None
