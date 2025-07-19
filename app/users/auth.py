# STDLIB
from datetime import UTC, datetime, timedelta

# THIRDPARTY
import jwt
from passlib.context import CryptContext
from pydantic import EmailStr

# FIRSTPARTY
from app.config import settings
from app.users.dao import UsersDAO

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)
    return encoded_jwt


async def authenticate_user(email: EmailStr, password: str):
    auth_user = await UsersDAO.find_one_or_none(email=email)
    if not auth_user:
        return None
    if not verify_password(password, auth_user.hashed_password):
        return None
    return auth_user
