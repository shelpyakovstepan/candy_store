# THIRDPARTY
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

# FIRSTPARTY
from app.users.dao import UsersDAO


class TestUsersDAO:
    @pytest.mark.parametrize(
        "user_chat_id",
        [
            (1111),
            (2222),
        ],
    )
    async def test_users_add(
        self,
        get_session: AsyncSession,
        user_chat_id: int,
    ):
        user = await UsersDAO.add(get_session, user_chat_id=user_chat_id)

        assert user is not None
        assert user.user_chat_id == user_chat_id

    @pytest.mark.parametrize(
        "user_id, exists",
        [
            (222222, True),
            (1000000, False),
        ],
    )
    async def test_find_by_id(
        self, get_session: AsyncSession, create_user, user_id, exists
    ):
        user = await UsersDAO.find_by_id(get_session, user_id)

        if exists:
            assert user.id == user_id
        else:
            assert not user

    @pytest.mark.parametrize(
        "user_id, user_chat_id, exists",
        [
            (222222, 11111, True),
            (1000000, 1000, False),
        ],
    )
    async def test_find_one_or_none(
        self, get_session: AsyncSession, create_user, user_id, user_chat_id, exists
    ):
        user = await UsersDAO.find_one_or_none(
            session=get_session, user_chat_id=user_chat_id
        )

        if exists:
            assert user.id == user_id
            assert user.user_chat_id == user_chat_id
        else:
            assert not user

    @pytest.mark.parametrize(
        "user_id, phone_number, exists",
        [
            (222222, "+79012345678", True),
            (1000000, "+79012345678", False),
        ],
    )
    async def test_users_update(
        self, get_session: AsyncSession, create_user, user_id, phone_number, exists
    ):
        user = await UsersDAO.update(
            get_session, model_id=user_id, phone_number=phone_number
        )

        if exists:
            assert user.id == user_id
            assert user.phone_number == phone_number
        else:
            assert not user


# pyright: reportOptionalMemberAccess=false
