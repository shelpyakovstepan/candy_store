# THIRDPARTY
from httpx import AsyncClient
import pytest


class TestUsersApi:
    @pytest.mark.parametrize(
        "email,phone_number,surname,name,password,status_code",
        [
            (
                "test@user.com",
                "+72227778899",
                "some_surname",
                "some_name",
                "ffffff",
                409,
            ),
            (
                "some@email.com",
                "+72227778899",
                "some_surname",
                "some_name",
                "ffffff",
                409,
            ),
            (
                "new@user.com",
                "+72227778449444444444",
                "some_very_big_surname",
                "some_name",
                "sssssss",
                422,
            ),
            (
                "new@user.com",
                "+72449",
                "some_very_big_surname",
                "some_name",
                "sssssss",
                422,
            ),
            (
                "new@user.com",
                "+72227778449",
                "some_very_big_surname",
                "some_name",
                "sssssss",
                422,
            ),
            (
                "new@user.com",
                "+72227778449",
                "some_surname",
                "some_very_big_big_big_name",
                "sssssss",
                422,
            ),
            ("new@user.com", "+72227778449", "some_surname", "some_name", "s", 422),
            (
                "new@user.com",
                "+72227778449",
                "some_surname",
                "some_name",
                "sssssssssssssssssssss",
                422,
            ),
            ("djdsaosi", "+72227778899", "some_surname", "some_name", "ffffff", 422),
        ],
    )
    async def test_register_user(
        self, email, phone_number, surname, name, password, status_code, ac: AsyncClient
    ):
        response = await ac.post(
            "/auth/register",
            json={
                "email": email,
                "phone_number": phone_number,
                "surname": surname,
                "name": name,
                "password": password,
            },
        )

        assert response.status_code == status_code

    @pytest.mark.parametrize(
        "email,password,status_code",
        [
            ("test@user.com", "kolobok", 200),
            ("test@user.com", "ffffff", 401),
            ("abcde", "kotopes", 422),
            ("test@t.com", "kolobok", 401),
        ],
    )
    async def test_login_user(self, email, password, status_code, ac: AsyncClient):
        response = await ac.post(
            "/auth/login", json={"email": email, "password": password}
        )

        assert response.status_code == status_code

    @pytest.mark.parametrize(
        "status_code_for_unauthorized_user,status_code_for_authorized_user",
        [(401, 200)],
    )
    async def test_get_me(
        self,
        status_code_for_unauthorized_user,
        status_code_for_authorized_user,
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
