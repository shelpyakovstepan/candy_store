# THIRDPARTY
from httpx import AsyncClient


class TestCartsApi:
    async def test_get_cart(
        self, create_user, create_cart, authenticated_ac: AsyncClient
    ):
        response = await authenticated_ac.get("/carts/")

        assert response.status_code == 200
