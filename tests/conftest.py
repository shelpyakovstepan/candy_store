# STDLIB
from typing import AsyncGenerator

# THIRDPARTY
import httpx
from httpx import AsyncClient
import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

# FIRSTPARTY
from app.database import async_session_maker
from app.main import app as fastapi_app
from app.users.models import Users

# @pytest.fixture(scope="session", autouse=True)
# async def prepare_database():
#  async with engine.begin() as connection:
#      await connection.execute(text("DROP TABLE users CASCADE"))
#      await connection.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="function")
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Фикстура для создания экземпляра сессии базы данных для тестов.

    Yields:
        AsyncSession: Асинхронная сессия SQLAlchemy для проведения тестов.
    """
    test_session = async_session_maker
    async with test_session() as t_session:
        try:
            yield t_session
        finally:
            await t_session.rollback()


@pytest.fixture(scope="function", autouse=True)
async def create_user(
    get_session: AsyncSession,
) -> AsyncGenerator[Users, None]:
    """Фикстура для создания тестового пользователя в БД.

    Args:
        get_session (AsyncSession): Асинхронная сессия базы данных

    Returns:
        Users: Экземпляр модели Users, представляющий созданного
        пользователя
    """
    id_ = 222222
    email = "test@user.com"
    phone_number = "+72227778899"
    surname = "Surname"
    name = "Name"
    hashed_password = "$2b$12$hTdYOVyjy.GCmFP2ArKncuG5Hg5Vlwh0qovYYNp10VRMc5129FmO6"
    is_admin = False
    user = Users(
        id=id_,
        email=email,
        phone_number=phone_number,
        surname=surname,
        name=name,
        hashed_password=hashed_password,
        is_admin=is_admin,
    )
    get_session.add(user)
    await get_session.commit()

    yield user

    # query = delete(ActivityModel).where(ActivityModel.user_id == id_)
    # await get_session.execute(query)
    query = delete(Users).where(Users.id == id_)
    await get_session.execute(query)
    await get_session.commit()


@pytest.fixture(scope="function")
async def ac():
    async with AsyncClient(
        base_url="http://test", transport=httpx.ASGITransport(app=fastapi_app)
    ) as ac:
        yield ac


@pytest.fixture(scope="function")
async def authenticated_ac():
    async with AsyncClient(
        base_url="http://test", transport=httpx.ASGITransport(app=fastapi_app)
    ) as ac:
        await ac.post(
            "/auth/login",
            json={"email": "test@user.com", "password": "kolobok"},
        )
        assert ac.cookies["access_token"]
        yield ac
