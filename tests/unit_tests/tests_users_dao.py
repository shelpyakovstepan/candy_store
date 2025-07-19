# THIRDPARTY
import pytest

# FIRSTPARTY
from app.users.dao import UsersDAO


class TestUsersDAO:
    @pytest.mark.parametrize(
        "user_id,email,exists",
        [
            (222222, "test@user.com", True),
            (1000000, "not@exists.com", False),
        ],
    )
    async def test_find_by_id(self, create_user, user_id, email, exists):
        user = await UsersDAO.find_by_id(user_id)

        if exists:
            assert user.id == user_id
            assert user.email == email
        else:
            assert not user

    @pytest.mark.parametrize(
        "user_id,email,exists",
        [
            (222222, "test@user.com", True),
            (1000000, "not@exists.com", False),
        ],
    )
    async def test_find_one_or_none(self, create_user, user_id, email, exists):
        user = await UsersDAO.find_one_or_none(email=email)

        if exists:
            assert user.id == user_id
            assert user.email == email
        else:
            assert not user


# pyright: reportOptionalMemberAccess=false
