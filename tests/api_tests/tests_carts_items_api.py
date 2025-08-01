# THIRDPARTY
from httpx import AsyncClient
import pytest


class TestCartsItemsApi:
    @pytest.mark.parametrize(
        "product_id,quantity,status_code",
        [
            (222222, 4, 200),
        ],
    )
    async def test_right_add_cart_item(
        self,
        create_user,
        create_product,
        create_cart,
        product_id,
        quantity,
        status_code,
        authenticated_ac: AsyncClient,
    ):
        response = await authenticated_ac.post(
            "/cartsitems/add", params={"product_id": product_id, "quantity": quantity}
        )

        assert response.status_code == status_code

    @pytest.mark.parametrize(
        "product_id,quantity,status_code",
        [
            (333333, 3, 409),
            ("one", 3, 422),
            (222222, 0, 422),
            (222222, 1, 400),
            (222222, 7, 400),
            (222222, 4, 409),
        ],
    )
    async def test_wrong_add_cart_item(
        self,
        create_user,
        create_product,
        create_cart,
        create_carts_item,
        product_id,
        quantity,
        status_code,
        authenticated_ac: AsyncClient,
    ):
        response = await authenticated_ac.post(
            "/cartsitems/add", params={"product_id": product_id, "quantity": quantity}
        )

        assert response.status_code == status_code

    async def test_get_all_cart_items(
        self,
        create_user,
        create_product,
        create_cart,
        create_carts_item,
        authenticated_ac: AsyncClient,
    ):
        response = await authenticated_ac.get("/cartsitems/")

        assert response.status_code == 200
        assert len(response.json()) == 1

    @pytest.mark.parametrize(
        "cart_item_id,status_code",
        [
            (333333, 409),
            ("one", 422),
            (222222, 200),
        ],
    )
    async def test_get_cart_item_by_id(
        self,
        create_user,
        create_product,
        create_cart,
        create_carts_item,
        cart_item_id,
        status_code,
        authenticated_ac: AsyncClient,
    ):
        response = await authenticated_ac.get(
            f"/cartsitems/{cart_item_id}",
            params={"cart_item_id": cart_item_id},
        )

        assert response.status_code == status_code

    @pytest.mark.parametrize(
        "cart_item_id,action,quantity,status_code",
        [
            (222222, "something-wrong", 1, 422),
            (22222, "increase", 0, 422),
            (333333, "reduce", 1, 409),
            (222222, "reduce", 5, 400),
            (222222, "increase", 7, 400),
            (222222, "increase", 1, 200),
            (222222, "reduce", 1, 200),
        ],
    )
    async def test_update_carts_items_quantity(
        self,
        create_user,
        create_product,
        create_cart,
        create_carts_item,
        cart_item_id,
        action,
        quantity,
        status_code,
        authenticated_ac: AsyncClient,
    ):
        response = await authenticated_ac.patch(
            "/cartsitems/update",
            params={
                "cart_item_id": cart_item_id,
                "action": action,
                "quantity": quantity,
            },
        )

        assert response.status_code == status_code

    @pytest.mark.parametrize(
        "carts_item_id,status_code",
        [
            (333333, 409),
            ("one", 422),
            (222222, 200),
        ],
    )
    async def test_delete_carts_item(
        self,
        create_user,
        create_product,
        create_cart,
        create_carts_item,
        carts_item_id,
        status_code,
        authenticated_ac: AsyncClient,
    ):
        response = await authenticated_ac.delete(
            f"/cartsitems/delete/{carts_item_id}",
            params={"carts_item_id": carts_item_id},
        )

        assert response.status_code == status_code
