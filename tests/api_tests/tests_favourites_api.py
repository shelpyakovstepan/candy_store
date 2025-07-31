# THIRDPARTY
from httpx import AsyncClient
import pytest


class TestFavouritesApi:
    @pytest.mark.parametrize("product_id, status", [(222222, 200)])
    async def test_right_add_favourite(
        self,
        create_user,
        create_product,
        authenticated_ac: AsyncClient,
        product_id,
        status,
    ):
        response = await authenticated_ac.post(
            f"/favourites/{product_id}", params={"product_id": product_id}
        )

        assert response.status_code == status

    @pytest.mark.parametrize(
        "product_id, status", [(222222, 409), (999999, 409), ("one", 422)]
    )
    async def test_wrong_add_favourite(
        self,
        create_user,
        create_product,
        create_favourite,
        authenticated_ac: AsyncClient,
        product_id,
        status,
    ):
        response = await authenticated_ac.post(
            f"/favourites/{product_id}", params={"product_id": product_id}
        )

        assert response.status_code == status

    async def test_get_favourites(
        self,
        create_user,
        create_product,
        create_favourite,
        authenticated_ac: AsyncClient,
    ):
        response = await authenticated_ac.get("/favourites")

        assert response.status_code == 200
        assert response.json() is not None

    @pytest.mark.parametrize("favourite_id, status", [(222222, 200), (999999, 409)])
    async def test_delete_favourite(
        self,
        create_user,
        create_product,
        create_favourite,
        authenticated_ac: AsyncClient,
        favourite_id,
        status,
    ):
        response = await authenticated_ac.delete(
            "/favourites/", params={"favourite_id": favourite_id}
        )

        assert response.status_code == status
