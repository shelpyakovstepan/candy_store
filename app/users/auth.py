# STDLIB
from datetime import UTC, datetime, timedelta

# THIRDPARTY
import jwt

# FIRSTPARTY
from app.config import settings


def create_access_token(data: dict) -> str:
    """
    Создаёт JWT токен.

    Args:
        data: Данные для создания JWT токена.

    Returns:
        encoded_jwt: Созданный JWT токен.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)
    return encoded_jwt
