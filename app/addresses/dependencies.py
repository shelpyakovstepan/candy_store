# THIRDPARTY
from fastapi import Depends

# FIRSTPARTY
from app.addresses.dao import AddressesDAO
from app.exceptions import NotAddressException
from app.users.dependencies import get_current_user
from app.users.models import Users


async def get_users_address(user: Users = Depends(get_current_user)):
    address = await AddressesDAO.find_one_or_none(user_id=user.id)
    if not address:
        raise NotAddressException

    return address
