# THIRDPARTY
from fastapi import APIRouter, Depends

# FIRSTPARTY
from app.addresses.dao import AddressesDAO
from app.exceptions import AddressAlreadyExistsException, NotAddressException
from app.users.dependencies import get_current_user
from app.users.models import Users

router = APIRouter(
    prefix="/addresses",
    tags=["Адресы"],
)


@router.post("")
async def create_address(
    street: str,
    house: int,
    building: int,
    flat: int,
    entrance: int,
    user: Users = Depends(get_current_user),
):
    """Город по умолчанию: Санкт-Петербург"""
    check_stored_address = await AddressesDAO.find_one_or_none(user_id=user.id)
    if check_stored_address:
        raise AddressAlreadyExistsException

    address = await AddressesDAO.add(
        user_id=user.id,
        city="SAINT_PETERSBURG",
        street=street,
        house=house,
        building=building,
        flat=flat,
        entrance=entrance,
    )

    return address


@router.get("/get")
async def get_address(
    user: Users = Depends(get_current_user),
):
    address = await AddressesDAO.find_one_or_none(user_id=user.id)
    if not address:
        raise NotAddressException

    return address


@router.put("/")
async def update_address(
    street: str,
    house: int,
    building: int,
    flat: int,
    entrance: int,
    user: Users = Depends(get_current_user),
):
    stored_address = await AddressesDAO.find_one_or_none(user_id=user.id)
    if not stored_address:
        raise NotAddressException

    address = await AddressesDAO.update(
        stored_address.id,
        street=street,
        house=house,
        building=building,
        flat=flat,
        entrance=entrance,
    )

    return address


@router.delete("//")
async def delete_address(user: Users = Depends(get_current_user)):
    stored_address = await AddressesDAO.find_one_or_none(user_id=user.id)
    if not stored_address:
        raise NotAddressException

    await AddressesDAO.delete(user_id=user.id)
