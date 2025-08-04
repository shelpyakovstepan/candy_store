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
from app.users.schemas import SPhoneNumber, SUsersWithPhoneNumber

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
    """Осуществляет аутентификацию и авторизацию пользователя через Телеграм"""
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
    """Осуществляет выход пользователя из системы"""
    response = RedirectResponse("/")
    response.delete_cookie(
        key="access_token",
    )
    return response


@router.get("/me")
async def get_me(user: Users = Depends(get_current_user)):
    """
    Выдаёт информацию пользователю о самом себе.

    Args:
        user: Экземпляр модели Users, представляющий текущего пользователя, полученный через зависимость get_current_user().

    Returns:
        user: Экземпляр модели Users, представляющий пользователя.
    """
    return user


@router.patch("/")
async def add_phone_number(
    session: DbSession,
    phone_number_data: SPhoneNumber = Depends(),
    user: Users = Depends(get_current_user),
) -> SUsersWithPhoneNumber:
    """
    Добавляет/Изменяет номер телефона.

    Args:
        session: DbSession(AsyncSession) - Асинхронная сессия базы данных.
        phone_number_data: Pydantic модель SPhoneNumber, содержащая данные для добавления/измененения номера телефона.
        user: Экземпляр модели Users, представляющий текущего пользователя, полученный через зависимость get_current_user().

    Returns:
        user: Экземпляр модели Users, представляющий пользователя с добавленным/изменнённым номером телефона.
    """
    user = await UsersDAO.update(  # pyright: ignore [reportAssignmentType]
        session, model_id=user.id, phone_number=phone_number_data.phone_number
    )

    return user
