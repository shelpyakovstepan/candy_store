# THIRDPARTY
from httpx import AsyncClient
import pytest


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
