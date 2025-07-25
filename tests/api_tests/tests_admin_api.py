# THIRDPARTY
from httpx import AsyncClient
import pytest


class TestAdminApi:
    @pytest.mark.parametrize(
        "name,category,ingredients,unit,price,min_quantity,max_quantity,description,image_id,status_code",
        [
            (
                "name",
                "wrong_category",
                ["ingredient"],
                "PIECES",
                2500,
                2,
                6,
                "description",
                1,
                422,
            ),
            (
                "name",
                "Торты",
                ["ingredient"],
                "wrong_unit",
                2500,
                2,
                6,
                "description",
                1,
                422,
            ),
            # ("Торт обычный", "Торты", "KILOGRAMS", 2500, 2, 6, "description", 1, 409),
        ],
    )
    async def test_add_product(
        self,
        create_user,
        create_product,
        name,
        category,
        ingredients,
        unit,
        price,
        min_quantity,
        max_quantity,
        description,
        image_id,
        status_code,
        authenticated_ac: AsyncClient,
    ):
        response = await authenticated_ac.post(
            "/admins/product",
            params={
                "name": name,
                "category": category,
                "unit": unit,
                "price": price,
                "min_quantity": min_quantity,
                "max_quantity": max_quantity,
                "description": description,
                "image_id": image_id,
            },
        )

        assert response.status_code == status_code

    @pytest.mark.parametrize(
        "product_id,name,category,unit,price,min_quantity,max_quantity,description,image_id,status_code",
        [
            (
                222222,
                "name",
                "wrong_category",
                "PIECES",
                2500,
                2,
                6,
                "description",
                1,
                422,
            ),
            (222222, "name", "Торты", "wrong_unit", 2500, 2, 6, "description", 1, 422),
            (333333, "name", "Торты", "KILOGRAMS", 2500, 2, 6, "description", 1, 409),
        ],
    )
    async def test_update_product(
        self,
        create_user,
        create_product,
        authenticated_ac: AsyncClient,
        product_id,
        name,
        category,
        unit,
        price,
        min_quantity,
        max_quantity,
        description,
        image_id,
        status_code,
    ):
        response = await authenticated_ac.patch(
            f"/admins/product/{product_id}",
            params={
                "product_id": product_id,
                "name": name,
                "category": category,
                "unit": unit,
                "price": price,
                "min_quantity": min_quantity,
                "max_quantity": max_quantity,
                "description": description,
                "image_id": image_id,
            },
        )

        assert response.status_code == status_code

    @pytest.mark.parametrize(
        "product_id, status_code", [(222222, 200), (333333, 409), ("one", 422)]
    )
    async def test_delete_product(
        self,
        create_user,
        create_product,
        authenticated_ac: AsyncClient,
        product_id,
        status_code,
    ):
        response = await authenticated_ac.delete(
            "/admins/", params={"product_id": product_id}
        )

        assert response.status_code == status_code

    @pytest.mark.parametrize(
        "status__in, status_code", [("WAITING", 200), ("WRONG_STATUS", 422)]
    )
    async def test_get_all_users_orders(
        self,
        create_user,
        create_product,
        create_address,
        create_cart,
        create_carts_item,
        create_order,
        status__in,
        status_code,
        authenticated_ac: AsyncClient,
    ):
        response = await authenticated_ac.get(
            "/admins/orders", params={"status__in": status__in}
        )

        assert response.status_code == status_code

    @pytest.mark.parametrize(
        "order_id, status, status_code",
        [(222222, "WRONG_STATUS", 422), (888888, "READY", 409)],
    )
    async def test_change_order_status(
        self,
        create_user,
        create_product,
        create_address,
        create_cart,
        create_carts_item,
        create_order,
        authenticated_ac: AsyncClient,
        order_id,
        status,
        status_code,
    ):
        response = await authenticated_ac.patch(
            f"/admins/update/{order_id}",
            params={
                "order_id": order_id,
                "status": status,
            },
        )

        assert response.status_code == status_code

    @pytest.mark.parametrize(
        "user_id, admin_status, status_code",
        [(333333, False, 409), (222222, True, 200)],
    )
    async def test_change_admin_status(
        self,
        create_user,
        create_product,
        authenticated_ac: AsyncClient,
        user_id,
        admin_status,
        status_code,
    ):
        response = await authenticated_ac.patch(
            "/admins//", params={"user_id": user_id, "admin_status": admin_status}
        )

        assert response.status_code == status_code
