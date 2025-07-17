# THIRDPARTY
from httpx import AsyncClient
import pytest


class TestAddressApi:
    @pytest.mark.parametrize(
        "street,house,building,flat,entrance,status_code",
        [
            ("Улица", 1, 1, 1, 1, 409),
            ("Улица", "one", 1, 1, 1, 422),
        ],
    )
    async def test_create_address(
        self,
        create_user,
        create_address,
        street,
        house,
        building,
        flat,
        entrance,
        status_code,
        authenticated_ac: AsyncClient,
    ):
        response = await authenticated_ac.post(
            "/addresses",
            params={
                "street": street,
                "house": house,
                "building": building,
                "flat": flat,
                "entrance": entrance,
            },
        )

        assert response.status_code == status_code

    async def test_get_address(
        self, create_user, create_address, authenticated_ac: AsyncClient
    ):
        response = await authenticated_ac.get("/addresses/get")

        assert response is not None
        assert response.status_code == 200

    @pytest.mark.parametrize(
        "street,house,building,flat,entrance,status_code",
        [
            ("Улица", 2, 1, 1, 1, 200),
            ("Улица", "one", 1, 1, 1, 422),
        ],
    )
    async def test_update_address(
        self,
        create_user,
        create_address,
        street,
        house,
        building,
        flat,
        entrance,
        status_code,
        authenticated_ac: AsyncClient,
    ):
        response = await authenticated_ac.put(
            "/addresses/",
            params={
                "street": street,
                "house": house,
                "building": building,
                "flat": flat,
                "entrance": entrance,
            },
        )

        assert response.status_code == status_code

    async def test_delete_address(
        self, create_user, create_address, authenticated_ac: AsyncClient
    ):
        response = await authenticated_ac.delete("/addresses//")

        assert response.status_code == 200
