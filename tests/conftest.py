# STDLIB
from datetime import datetime
from typing import AsyncGenerator

# THIRDPARTY
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import httpx
from httpx import AsyncClient, Cookies
import pytest
from redis import asyncio as aioredis
from sqlalchemy import and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

# FIRSTPARTY
from app.addresses.models import Addresses, CityEnum
from app.carts.models import Carts, StatusCartEnum
from app.cartsItems.models import CartsItems
from app.config import get_redis_url
from app.database import SessionLocal
from app.favourites.models import Favourites
from app.logger import logger
from app.main import app as fastapi_app
from app.orders.models import (
    Orders,
    PaymentMethodEnum,
    ReceivingMethodEnum,
    StatusEnum,
)
from app.products.models import Products, UnitEnum
from app.purchases.models import Purchases
from app.users.auth import create_access_token
from app.users.models import Users

# @pytest.fixture(scope="session", autouse=True)
# async def prepare_database():
#    async with engine.begin() as connection:
#        await connection.execute(text("DROP TABLE orders CASCADE"))
#        await connection.execute(text("DROP TABLE addresses CASCADE"))
#        await connection.execute(text("DROP TABLE favourites CASCADE"))
#        query = delete(CartsItems)
#        await connection.execute(query)
#        await connection.execute(text("DROP TABLE products CASCADE"))
#        await connection.execute(text("DROP TABLE carts CASCADE"))
#        await connection.execute(text("DROP TABLE users CASCADE"))
#        await connection.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="function")
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Фикстура для создания экземпляра сессии базы данных для тестов.

    Yields:
        AsyncSession: Асинхронная сессия SQLAlchemy для проведения тестов.
    """
    test_session = SessionLocal
    async with test_session() as session:
        try:
            yield session
        finally:
            await session.rollback()


@pytest.fixture(scope="function")
async def get_redis():
    """Фикстура для создания Redis для тестов.

    Yields:
        Подключение к Redis.
    """
    redis = aioredis.from_url(get_redis_url())
    FastAPICache.init(RedisBackend(redis), prefix="test_fastapi-cache")

    try:
        response = await redis.ping()
        if response:
            logger.info("Подключение к Redis успешно!")
        else:
            logger.error("Не удалось подключиться к Redis.")
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")

    yield redis

    await redis.aclose()


@pytest.fixture
async def create_user(
    get_session: AsyncSession,
) -> AsyncGenerator[Users, None]:
    """Фикстура для создания тестового пользователя в БД.

    Args:
        get_session (AsyncSession): Асинхронная сессия базы данных.

    Returns:
        Users: Экземпляр модели Users, представляющий созданного
        пользователя.
    """
    id_ = 222222
    user_chat_id = 11111
    is_admin = True
    user = Users(
        id=id_,
        user_chat_id=user_chat_id,
        is_admin=is_admin,
    )
    get_session.add(user)
    await get_session.commit()

    yield user

    delete_purchases_query = delete(Purchases).where(Purchases.user_id == id_)
    await get_session.execute(delete_purchases_query)

    delete_orders_query = delete(Orders).where(and_(Orders.user_id == id_))
    await get_session.execute(delete_orders_query)

    delete_carts_items_query = delete(CartsItems).where(CartsItems.cart_id == 222222)
    await get_session.execute(delete_carts_items_query)

    delete_cart_query = delete(Carts).where(Carts.user_id == id_)
    await get_session.execute(delete_cart_query)

    delete_address_query = delete(Addresses).where(Addresses.user_id == id_)
    await get_session.execute(delete_address_query)

    delete_favourites_items_query = delete(Favourites).where(Favourites.user_id == id_)
    await get_session.execute(delete_favourites_items_query)

    query = delete(Users).where(
        and_(
            Users.id == id_,
        )
    )
    await get_session.execute(query)
    await get_session.commit()


@pytest.fixture
async def create_address(
    get_session: AsyncSession,
    create_user: Users,
) -> AsyncGenerator[Addresses, None]:
    """Фикстура для создания тестового адреса пользователя в БД.

    Args:
        get_session (AsyncSession): Асинхронная сессия базы данных.
        create_user: Экземпляр модели Users.

    Returns:
        Addresses: Экземпляр модели Addresses, представляющий созданный
        адрес.
    """
    id_ = 222222
    user_id = 222222
    city = CityEnum.SAINT_PETERSBURG
    street = "Невский проспект"
    house = 1
    building = 1
    flat = 1
    entrance = 1
    status = True

    address = Addresses(
        id=id_,
        user_id=user_id,
        city=city,
        street=street,
        house=house,
        building=building,
        flat=flat,
        entrance=entrance,
        status=status,
    )

    get_session.add(address)
    await get_session.commit()

    yield address

    query = delete(Addresses).where(
        and_(
            Addresses.id == id_,
        )
    )
    await get_session.execute(query)
    await get_session.commit()


@pytest.fixture
async def create_cart(
    get_session: AsyncSession,
    create_user: Users,
) -> AsyncGenerator[Carts, None]:
    """Фикстура для создания тестовой корзины в БД.

    Args:
        get_session (AsyncSession): Асинхронная сессия базы данных.
        create_user: Экземпляр модели Users.

    Returns:
        Carts: Экземпляр модели Carts, представляющий созданную
        корзину.
    """
    id_ = 222222
    user_id = 222222
    total_price = 5000
    status = StatusCartEnum.ACTIVE

    cart = Carts(
        id=id_,
        user_id=user_id,
        total_price=total_price,
        status=status,
    )

    get_session.add(cart)
    await get_session.commit()

    yield cart

    delete_carts_items_query = delete(CartsItems).where(CartsItems.cart_id == id_)
    await get_session.execute(delete_carts_items_query)

    delete_orders_query = delete(Orders).where(and_(Orders.user_id == id_))
    await get_session.execute(delete_orders_query)

    query = delete(Carts).where(and_(Carts.id == id_))
    await get_session.execute(query)
    await get_session.commit()


@pytest.fixture
async def create_product(
    get_session: AsyncSession,
) -> AsyncGenerator[Products, None]:
    """Фикстура для создания тестового продукта в БД.

    Args:
        get_session (AsyncSession): Асинхронная сессия базы данных.

    Returns:
        Products: Экземпляр модели Products, представляющий созданный
        продукт.
    """
    id_ = 222222
    name = "Торт обычный"
    category = "Торты"
    ingredients = ["Шоколад", "Ягоды"]
    unit = UnitEnum.KILOGRAMS
    price = 2500
    min_quantity = 2
    max_quantity = 6
    description = "Какой то тортик"
    image_id = 1

    product = Products(
        id=id_,
        name=name,
        category=category,
        ingredients=ingredients,
        unit=unit,
        price=price,
        min_quantity=min_quantity,
        max_quantity=max_quantity,
        description=description,
        image_id=image_id,
    )

    get_session.add(product)
    await get_session.commit()

    yield product

    delete_favourites_items_query = delete(Favourites).where(
        Favourites.product_id == id_
    )
    await get_session.execute(delete_favourites_items_query)

    delete_carts_items_query = delete(CartsItems).where(CartsItems.product_id == id_)
    await get_session.execute(delete_carts_items_query)
    query = delete(Products).where(
        and_(
            Products.id == id_,
        )
    )
    await get_session.execute(query)
    await get_session.commit()


@pytest.fixture
async def create_favourite(
    get_session: AsyncSession,
    create_user: Users,
) -> AsyncGenerator[Carts, None]:
    """Фикстура для создания тестовой позиции в избранном в БД.

    Args:
        get_session (AsyncSession): Асинхронная сессия базы данных
        create_user: Экземпляр модели Users.

    Returns:
        Carts: Экземпляр модели Favourites, представляющий созданную
        позицию в избранном.
    """
    id_ = 222222
    user_id = 222222
    product_id = 222222

    favourite = Favourites(
        id=id_,
        user_id=user_id,
        product_id=product_id,
    )

    get_session.add(favourite)
    await get_session.commit()

    yield favourite

    delete_favourites_items_query = delete(Favourites).where(Favourites.id == id_)
    await get_session.execute(delete_favourites_items_query)
    await get_session.commit()


@pytest.fixture
async def create_carts_item(
    get_session: AsyncSession,
    create_cart: Carts,
) -> AsyncGenerator[CartsItems, None]:
    """Фикстура для создания тестового товара в корзине в БД.

    Args:
        get_session (AsyncSession): Асинхронная сессия базы данных.
        create_cart: Экземпляр модели Carts.

    Returns:
        CartsItems: Экземпляр модели CartsItems, представляющий созданный
        товар в корзине.
    """
    id_ = 222222
    product_id = 222222
    cart_id = 222222
    quantity = 3

    carts_item = CartsItems(
        id=id_,
        product_id=product_id,
        cart_id=cart_id,
        quantity=quantity,
    )

    get_session.add(carts_item)
    await get_session.commit()

    yield carts_item

    query = delete(CartsItems).where(
        CartsItems.id == id_,
    )
    await get_session.execute(query)

    await get_session.commit()


@pytest.fixture
async def create_order(
    get_session: AsyncSession,
    create_cart: Carts,
) -> AsyncGenerator[Orders, None]:
    """Фикстура для создания тестовой корзины в БД.

    Args:
        get_session (AsyncSession): Асинхронная сессия базы данных.
        create_cart: Экземпляр модели Carts.

    Returns:
        Orders: Экземпляр модели Orders, представляющий созданный
        заказ.
    """
    id_ = 222222
    user_id = 222222
    created_at = datetime.strptime("2025-07-17", "%Y-%m-%d")
    cart_id = 222222
    address = 222222
    date_receiving = datetime.strptime("2025-07-21", "%Y-%m-%d")
    time_receiving = datetime.strptime("12:00", "%H:%M").time()
    receiving_method = ReceivingMethodEnum.PICKUP
    comment = "Comment"
    payment = PaymentMethodEnum.NONCASH
    total_price = 5000
    status = StatusEnum.WAITING

    order = Orders(
        id=id_,
        user_id=user_id,
        created_at=created_at,
        cart_id=cart_id,
        address=address,
        date_receiving=date_receiving,
        time_receiving=time_receiving,
        receiving_method=receiving_method,
        comment=comment,
        payment=payment,
        total_price=total_price,
        status=status,
    )

    get_session.add(order)
    await get_session.commit()

    yield order

    delete_purchases_query = delete(Purchases).where(Purchases.order_id == id_)
    await get_session.execute(delete_purchases_query)

    delete_orders_query = delete(Orders).where(and_(Orders.id == id_))
    await get_session.execute(delete_orders_query)

    await get_session.commit()


@pytest.fixture(scope="function")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    """Отдаёт неаутентифицированного пользователя."""
    async with AsyncClient(
        base_url="http://test", transport=httpx.ASGITransport(app=fastapi_app)
    ) as ac:
        yield ac


@pytest.fixture(scope="function")
async def authenticated_ac(create_user) -> AsyncGenerator[AsyncClient, None]:
    """Отдаёт аутентифицированного пользователя."""
    async with AsyncClient(
        base_url="http://test", transport=httpx.ASGITransport(app=fastapi_app)
    ) as ac:
        access_token = create_access_token({"sub": str(create_user.id)})

        ac.cookies = Cookies()
        ac.cookies.set("access_token", access_token)
        assert ac.cookies["access_token"]
        yield ac

        ac.cookies.clear()
