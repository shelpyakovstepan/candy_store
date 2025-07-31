# STDLIB
import hmac
from typing import Annotated

# THIRDPARTY
from fastapi import APIRouter, Depends, Query
from fastapi.requests import Request
from fastapi.responses import PlainTextResponse, RedirectResponse

# FIRSTPARTY
from app.config import get_bot_token_hash
from app.database import DbSession
from app.logger import logger
from app.users.auth import create_access_token
from app.users.dao import UsersDAO
from app.users.dependencies import get_current_user
from app.users.models import Users

router = APIRouter(
    prefix="/auth",
    tags=["Аутентификация & Пользователи"],
)


@router.get("/telegram-callback")
async def telegram_callback(
    session: DbSession,
    request: Request,
    user_id: Annotated[int, Query(alias="id")],
    query_hash: Annotated[str, Query(alias="hash")],
    next_url: Annotated[str, Query(alias="next")] = "/",
):
    params = request.query_params.items()
    data_check_string = "\n".join(
        sorted(f"{x}={y}" for x, y in params if x not in ("hash", "next"))
    )
    computed_hash = hmac.new(
        get_bot_token_hash().digest(), data_check_string.encode(), "sha256"
    ).hexdigest()
    is_correct = hmac.compare_digest(computed_hash, query_hash)
    if not is_correct:
        return PlainTextResponse(
            "Authorization failed. Please try again", status_code=401
        )

    new_user = await UsersDAO.find_one_or_none(session, user_chat_id=user_id)
    if not new_user:
        new_user = await UsersDAO.add(
            session,
            user_chat_id=user_id,
        )
        logger.info("User successfully registered")

    access_token = create_access_token({"sub": str(new_user.id)})  # pyright: ignore [reportOptionalMemberAccess]

    response = RedirectResponse(next_url)
    response.set_cookie("access_token", access_token, httponly=True)
    return response


@router.get("/logout")
async def logout():
    response = RedirectResponse("/")
    response.delete_cookie(
        key="access_token",
    )
    return response


@router.get("/me")
async def get_me(user: Users = Depends(get_current_user)):
    """Выдаёт информацию пользователю о самом себе."""
    return user
