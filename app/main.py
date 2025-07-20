# STDLIB
from contextlib import asynccontextmanager
import time
from typing import AsyncIterator

# THIRDPARTY
from fastapi import FastAPI, Request
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

# FIRSTPARTY
from app.addresses.router import router as addresses_router
from app.admin.router import router as admins_router
from app.cartsItems.router import router as carts_items_router
from app.config import get_redis_url
from app.database import check_db_connection
from app.logger import logger
from app.orders.router import router as orders_router
from app.products.router import router as products_router
from app.users.router import router as users_router


async def redis_connection():
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

    yield


app = FastAPI(lifespan=lifespan)

# Проверка подключения

app.include_router(users_router)
app.include_router(admins_router)
app.include_router(addresses_router)

app.include_router(products_router)

app.include_router(carts_items_router)

app.include_router(orders_router)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"Request handling time: {round(process_time, 4)}")
    return response
