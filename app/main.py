# STDLIB
from contextlib import asynccontextmanager
from typing import AsyncIterator

# THIRDPARTY
from fastapi import APIRouter, FastAPI

# FIRSTPARTY
from app.database import check_db_connection
from app.users.router import router as users_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await check_db_connection()
    yield


app = FastAPI(lifespan=lifespan)

router = APIRouter(
    prefix="/test",
    tags=["api"],
)


@router.get("//")
async def ping():
    return {"data": "pong"}


app.include_router(router)
app.include_router(users_router)
