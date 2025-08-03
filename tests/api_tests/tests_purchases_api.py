# THIRDPARTY
from httpx import AsyncClient
import pytest


class TestPurchasesApi:
    @pytest.mark.parametrize(
        "request_, status_code",
        [
            (None, 400),
            ("http://localhost:8000/", 400),
        ],
    )
    async def test_robokassa_result(
        self,
        create_user,
        authenticated_ac: AsyncClient,
        request_,
        status_code,
    ):
        response = await authenticated_ac.post(
            "/purchases/result/", params={"request": request_}
        )

        assert response.status_code == status_code
