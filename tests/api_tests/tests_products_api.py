# THIRDPARTY
from httpx import AsyncClient
import pytest


class TestProductsApi:
    @pytest.mark.parametrize(
        "page,page_size",
        [
            (1, 5),
        ],
    )
    async def test_get_products(
        self, get_redis, create_product, page, page_size, ac: AsyncClient
    ):
        response = await ac.get(
            "/products/",
            params={
                "page": page,
                "page_size": page_size,
            },
        )

        assert response is not None
        assert response.status_code == 200

    @pytest.mark.parametrize(
        "product_id,status_code", [(222222, 200), (777777, 409), ("one", 422)]
    )
    async def test_get_product_by_id(
        self, create_product, product_id, status_code, ac: AsyncClient
    ):
        response = await ac.get(
            f"/products/{product_id}", params={"product_id": product_id}
        )

        assert response.status_code == status_code
