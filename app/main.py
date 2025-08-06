# STDLIB
from contextlib import asynccontextmanager
import time
from typing import AsyncIterator
import urllib.parse

# THIRDPARTY
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from sqladmin import Admin

# FIRSTPARTY
from app.addresses.router import router as addresses_router
from app.admin.router import router as admins_router
from app.admin_app.auth import authentication_backend
from app.admin_app.views import (
    AddressesAdmin,
    CartsAdmin,
    CartsItemsAdmin,
    FavouritesAdmin,
    OrdersAdmin,
    ProductsAdmin,
    PurchasesAdmin,
    UsersAdmin,
)
from app.carts.router import router as carts_router
from app.cartsItems.router import router as carts_items_router
from app.config import get_redis_url
from app.database import check_db_connection, engine
from app.favourites.router import router as favourites_router
from app.logger import logger
from app.orders.router import router as orders_router
from app.products.router import router as products_router
from app.purchases.router import router as purchases_router
from app.rabbitmq.broker import broker
from app.users.router import router as users_router


async def redis_connection():
    """Проверяет подключение к Redis."""
    redis = aioredis.from_url(get_redis_url())
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

    try:
        response = await redis.ping()
        if response:
            logger.info("Подключение к Redis успешно!")
        else:
            logger.error("Не удалось подключиться к Redis.")
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
        raise e


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await check_db_connection()
    await redis_connection()
    await broker.connect()

    yield


app = FastAPI(lifespan=lifespan)

admin = Admin(app, engine, authentication_backend=authentication_backend)

admin.add_view(UsersAdmin)
admin.add_view(AddressesAdmin)
admin.add_view(ProductsAdmin)
admin.add_view(FavouritesAdmin)
admin.add_view(CartsAdmin)
admin.add_view(CartsItemsAdmin)
admin.add_view(OrdersAdmin)
admin.add_view(PurchasesAdmin)
app.include_router(users_router)
app.include_router(admins_router)
app.include_router(addresses_router)

app.include_router(products_router)
app.include_router(favourites_router)
app.include_router(carts_router)

app.include_router(carts_items_router)

app.include_router(orders_router)
app.include_router(purchases_router)

templates = Jinja2Templates("app/templates")

app.mount("", users_router)


@app.middleware("http")
async def middleware(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/auth/"):
        return response

    url_safe_path = urllib.parse.quote(request.url.path, safe="")
    template_context = {"request": request, "next_path": url_safe_path}
    login_wall = templates.TemplateResponse("login.html", template_context)

    token = request.cookies.get("access_token")
    if not token:
        return login_wall

    return response


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Определяет время выполнения любого запроса."""
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"Request handling time: {round(process_time, 4)}")
    return response
