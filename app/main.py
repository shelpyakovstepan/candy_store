# STDLIB
from contextlib import asynccontextmanager
import time
from typing import AsyncIterator

# THIRDPARTY
from fastapi import FastAPI, Request

# FIRSTPARTY
from app.addresses.router import router as addresses_router
from app.admin.router import router as admins_router
from app.database import check_db_connection
from app.logger import logger
from app.users.router import router as users_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await check_db_connection()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(users_router)
app.include_router(admins_router)
app.include_router(addresses_router)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"Request handling time: {round(process_time, 4)}")
    return response
