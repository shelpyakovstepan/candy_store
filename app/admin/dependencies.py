# THIRDPARTY
from fastapi import Depends

# FIRSTPARTY
from app.exceptions import NotEnoughRightsException
from app.users.dependencies import get_current_user
from app.users.models import Users


async def check_admin_status(user: Users = Depends(get_current_user)):
    """
    Проверяет статус админа пользователя.

    Args:
        user: Экземпляр модели Users, представляющий текущего пользователя, полученный через зависимость get_current_user().

    Returns:
        True, если пользователь является админом.
    """
    if not user.is_admin:
        raise NotEnoughRightsException
    return True
