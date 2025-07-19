# THIRDPARTY
import pytest

# FIRSTPARTY
from app.carts.dao import CartsDAO


class TestCartsDAO:
    async def test_carts_add(self, create_user):
        cart = await CartsDAO.add(user_id=create_user.id)

        assert cart is not None
        assert cart.user_id == create_user.id

    @pytest.mark.parametrize(
        "user_id, exists",
        [
            (222222, True),
            (333333, False),
        ],
    )
    async def test_carts_find_one_or_none(
        self, create_user, create_cart, user_id, exists
    ):
        cart = await CartsDAO.find_one_or_none(user_id=user_id)

        if exists:
            assert cart is not None
            assert cart.user_id == user_id
        else:
            assert cart is None
