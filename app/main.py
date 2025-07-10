# THIRDPARTY
from fastapi import APIRouter, FastAPI

app = FastAPI()

router = APIRouter(
    prefix="/test",
    tags=["api"],
)

# app.include_router(router)


@app.get("//")
async def ping():
    return {"data": "pong"}
