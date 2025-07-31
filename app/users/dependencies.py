# STDLIB
from datetime import UTC, datetime

# THIRDPARTY
from fastapi import Depends, Request
from jose import JWTError, jwt

# FIRSTPARTY
from app.config import settings
from app.database import DbSession
from app.exceptions import (
    IncorrectTokenFormatException,
    TokenAbsentException,
    TokenExpiredException,
    UserIsNotPresentException,
)
from app.users.dao import UsersDAO


def get_token(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise TokenAbsentException
    return token


async def get_current_user(session: DbSession, token: str = Depends(get_token)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)
    except JWTError:
        raise IncorrectTokenFormatException
    expire: str = payload.get("exp")  # pyright: ignore [reportAssignmentType]
    if (not expire) or int(expire) < datetime.now(UTC).timestamp():
        raise TokenExpiredException
    user_id: str = payload.get("sub")  # pyright: ignore [reportAssignmentType]
    if not user_id:
        raise UserIsNotPresentException
    user = await UsersDAO.find_by_id(session, int(user_id))
    if not user:
        raise UserIsNotPresentException

    return user
