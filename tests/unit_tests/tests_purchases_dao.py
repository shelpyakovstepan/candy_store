# THIRDPARTY
from httpx import AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

# FIRSTPARTY
from app.purchases.dao import PurchasesDAO


class TestPurchaseDAO:
    @pytest.mark.parametrize(
        "user_id, payment_id, price, order_id, payment_type",
        [(222222, "222222", 200, 222222, "robokassa")],
    )
    async def test_purchase_add(
        self,
        get_session: AsyncSession,
        create_user,
        create_address,
        create_product,
        create_cart,
        create_carts_item,
        create_order,
        authenticated_ac: AsyncClient,
        user_id,
        payment_id,
        price,
        order_id,
        payment_type,
    ):
        purchase = await PurchasesDAO.add(
            session=get_session,
            user_id=user_id,
            payment_id=payment_id,
            price=price,
            order_id=order_id,
            payment_type=payment_type,
        )

        assert purchase is not None
        assert purchase.user_id == user_id
        assert purchase.payment_id == payment_id
        assert purchase.price == price
        assert purchase.order_id == order_id
        assert purchase.payment_type == payment_type
