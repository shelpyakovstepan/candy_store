# THIRDPARTY
from httpx import AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession


class TestUsersApi:
    @pytest.mark.parametrize(
        "status_code_for_unauthorized_user,status_code_for_authorized_user",
        [(401, 200)],
    )
    async def test_get_me(
        self,
        status_code_for_unauthorized_user,
        status_code_for_authorized_user,
        create_user,
        ac: AsyncClient,
        authenticated_ac: AsyncClient,
    ):
        unauthorized_user_request_response = await ac.get("/auth/me")
        assert (
            unauthorized_user_request_response.status_code
            == status_code_for_unauthorized_user
        )

        authorized_user_request_response = await authenticated_ac.get("/auth/me")
        assert (
            authorized_user_request_response.status_code
            == status_code_for_authorized_user
        )

    @pytest.mark.parametrize(
        "phone_number, status_code",
        [
            ("wrong_number_format", 422),
            ("+79012345678", 200),
        ],
    )
    async def test_add_phone_number(
        self,
        get_session: AsyncSession,
        create_user,
        authenticated_ac: AsyncClient,
        phone_number,
        status_code,
    ):
        response = await authenticated_ac.patch(
            "/auth/", params={"phone_number": phone_number}
        )

        assert response.status_code == status_code
