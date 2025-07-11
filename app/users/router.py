# THIRDPARTY
from fastapi import APIRouter, Depends, Response

# FIRSTPARTY
from app.exceptions import (
    IncorrectUserEmailOrPasswordException,
    NotUserException,
    UserAlreadyExistsException,
)
from app.logger import logger
from app.users.auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
)
from app.users.dao import UserDAO
from app.users.dependencies import get_current_user
from app.users.models import Users
from app.users.schemas import SUsersLogin, SUsersRegister

router = APIRouter(prefix="/auth", tags=["Аутентификация & Пользователи"])


@router.post("/register")
async def register(user_data: SUsersRegister):
    """Создаёт нового пользователя."""
    existing_user_by_email = await UserDAO.find_one_or_none(email=user_data.email)
    existing_user_by_phone_number = await UserDAO.find_one_or_none(
        phone_number=user_data.phone_number
    )
    if existing_user_by_email or existing_user_by_phone_number:
        raise UserAlreadyExistsException

    hashed_password = get_password_hash(user_data.password)

    await UserDAO.add(
        email=user_data.email,
        phone_number=user_data.phone_number,
        surname=user_data.surname,
        name=user_data.name,
        hashed_password=hashed_password,
    )

    logger.debug("User successfully registered")


@router.post("/login")
async def login(response: Response, user_data: SUsersLogin):
    """Логинит пользователя в системе."""
    user = await authenticate_user(user_data.email, user_data.password)
    if not user:
        raise IncorrectUserEmailOrPasswordException

    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie("access_token", access_token, httponly=True)

    logger.debug("User logged in")

    return {"access_token": access_token}


@router.get("/me")
async def get_me(user: Users = Depends(get_current_user)):
    """Выдаёт информацию пользователю о самом себе."""
    return user


@router.post("/logout")
async def logout_user(response: Response):
    """Осуществляет выход пользователя из системы"""
    response.delete_cookie("access_token")
    logger.debug("User logged out")


@router.patch("/admins")
async def change_admin_status(user_id: int, admin_status: bool):
    """Изменяет статус админа пользователя."""
    user = await UserDAO.update_one(user_id, is_admin=admin_status)
    if not user:
        raise NotUserException

    return user  # pyright: ignore [reportReturnType]
