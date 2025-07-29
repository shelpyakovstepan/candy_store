# THIRDPARTY
from fastapi import APIRouter, Depends

# FIRSTPARTY
from app.addresses.dao import AddressesDAO
from app.addresses.dependencies import get_users_address
from app.addresses.schemas import SAddAndUpdateAddress, SAddresses
from app.exceptions import AddressAlreadyExistsException, NotAddressException
from app.users.dependencies import get_current_user
from app.users.models import Users

router = APIRouter(
    prefix="/addresses",
    tags=["Адресы"],
)


@router.post("")
async def create_address(
    address_data: SAddAndUpdateAddress = Depends(),
    user: Users = Depends(get_current_user),
) -> SAddresses:
    """
    Город по умолчанию: Санкт-Петербург.

    Создаёт адрес пользователя.

    Args:
        address_data: Pydantic модель SAddAndUpdateAddress, содержащая данные для добавления адреса пользователя.
        user: Экземпляр модели Users, представляющий текущего пользователя,
        полученный через зависимость get_current_user().

    Returns:
        address: Экземпляр модели Addresses, представляющий созданный адрес.
    """
    check_stored_address = await AddressesDAO.find_one_or_none(user_id=user.id)
    if check_stored_address:
        raise AddressAlreadyExistsException

    address = await AddressesDAO.add(
        user_id=user.id,
        city="SAINT_PETERSBURG",
        street=address_data.street,
        house=address_data.house,
        building=address_data.building,
        flat=address_data.flat,
        entrance=address_data.entrance,
    )

    return address


@router.get("/get")
async def get_address(address: SAddresses = Depends(get_users_address)) -> SAddresses:
    """
    Отдаёт текущий адрес пользователя.

    Args:
        address: Экземпляр модели Addresses, представляющий текущий адрес пользователя,
        полученный через зависимость get_users_address().

    Returns:
        address: Экземпляр модели Addresses, представляющий текущий адрес пользователя.
    """
    return address


@router.put("/")
async def update_address(
    address_data: SAddAndUpdateAddress = Depends(),
    user: Users = Depends(get_current_user),
) -> SAddresses:
    """
    Город по умолчанию: Санкт-Петербург.

    Изменяет адрес пользователя.

    Args:
        address_data: Pydantic модель SAddAndUpdateAddress, содержащая данные для изменения адреса пользователя.
        user: Экземпляр модели Users, представляющий текущего пользователя,
        полученный через зависимость get_current_user().

    Returns:
        address: Экземпляр модели Addresses, представляющий изменённый адрес.
    """
    stored_address = await AddressesDAO.find_one_or_none(user_id=user.id)
    if not stored_address:
        raise NotAddressException

    address = await AddressesDAO.update(
        stored_address.id,
        street=address_data.street,
        house=address_data.house,
        building=address_data.building,
        flat=address_data.flat,
        entrance=address_data.entrance,
    )

    return address
