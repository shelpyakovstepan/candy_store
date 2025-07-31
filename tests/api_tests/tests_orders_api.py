# THIRDPARTY
from httpx import AsyncClient
import pytest


class TestOrdersApi:
    @pytest.mark.parametrize(
        "date_receiving,time_receiving,receiving_method,payment,comment,status_code",
        [
            ("wrong_date_format", "12:00", "DELIVERY", "NONCASH", "comment", 422),
            ("2100-12-01", "wrong_time_format", "DELIVERY", "NONCASH", "comment", 422),
            (
                "2100-12-01",
                "12:00",
                "wrong_receiving_method_format",
                "NONCASH",
                "comment",
                422,
            ),
            ("2100-01-01", "12:00", "DELIVERY", "wrong_payment_format", "comment", 422),
            ("2000-01-01", "12:00", "DELIVERY", "NONCASH", "comment", 400),
            ("2100-01-01", "12:00", "DELIVERY", "CASH", "comment", 400),
            ("2100-01-01", "12:00", "DELIVERY", "NONCASH", "comment", 409),
        ],
    )
    async def test_wrong_create_order(
        self,
        create_user,
        create_address,
        create_product,
        create_cart,
        create_carts_item,
        create_order,
        authenticated_ac: AsyncClient,
        date_receiving,
        time_receiving,
        receiving_method,
        payment,
        comment,
        status_code,
    ):
        response = await authenticated_ac.post(
            "/orders/add",
            params={
                "date_receiving": date_receiving,
                "time_receiving": time_receiving,
                "receiving_method": receiving_method,
                "payment": payment,
                "comment": comment,
            },
        )

        assert response.status_code == status_code

    async def test_get_all_orders(
        self,
        create_user,
        create_address,
        create_product,
        create_cart,
        create_carts_item,
        create_order,
        authenticated_ac: AsyncClient,
    ):
        response = await authenticated_ac.get("/orders/")

        assert response.status_code == 200
        assert len(response.json()) == 1

    @pytest.mark.parametrize(
        "order_id,status_code",
        [
            (999999, 409),
        ],
    )
    async def test_pay_for_the_order(
        self,
        create_user,
        create_address,
        create_product,
        create_cart,
        create_carts_item,
        create_order,
        authenticated_ac: AsyncClient,
        order_id,
        status_code,
    ):
        response = await authenticated_ac.patch(
            "/orders/pay", params={"order_id": order_id}
        )

        assert response.status_code == status_code

    @pytest.mark.parametrize(
        "order_id,status_code",
        [
            (333333, 409),
            (222222, 200),
        ],
    )
    async def test_delete_order(
        self,
        create_user,
        create_address,
        create_product,
        create_cart,
        create_carts_item,
        create_order,
        authenticated_ac: AsyncClient,
        order_id,
        status_code,
    ):
        response = await authenticated_ac.delete(
            f"/orders/{order_id}",
            params={
                "order_id": order_id,
            },
        )

        assert response.status_code == status_code
