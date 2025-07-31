# THIRDPARTY
from fastapi import Depends

# FIRSTPARTY
from app.addresses.dao import AddressesDAO
from app.addresses.schemas import SAddresses
from app.database import DbSession
from app.exceptions import NotAddressException
from app.users.dependencies import get_current_user
from app.users.models import Users


async def get_users_address(
    session: DbSession, user: Users = Depends(get_current_user)
) -> SAddresses:
    """
    Отдаёт текущий адрес пользователя.

    Args:
        user: Экземпляр модели Users, представляющий текущего пользователя, полученный через зависимость get_current_user().

    Returns:
        address: Экземпляр модели Addresses, представляющий текущий адрес пользователя.
    """
    address = await AddressesDAO.find_one_or_none(session, user_id=user.id, status=True)
    if not address:
        raise NotAddressException

    return address
