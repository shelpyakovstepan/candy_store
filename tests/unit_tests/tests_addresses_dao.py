# THIRDPARTY
import pytest

# FIRSTPARTY
from app.addresses.dao import AddressesDAO


class TestAddressesDAO:
    @pytest.mark.parametrize(
        "user_id, city, street, house, building, flat, entrance",
        [(222222, "SAINT_PETERSBURG", "Улица", 1, 1, 1, 1)],
    )
    async def test_address_add(
        self, create_user, user_id, city, street, house, building, flat, entrance
    ):
        address = await AddressesDAO.add(
            user_id=user_id,
            city=city,
            street=street,
            house=house,
            building=building,
            flat=flat,
            entrance=entrance,
        )

        assert address is not None
        assert address.user_id == user_id
        assert address.street == street
        assert address.house == house
        assert address.building == building
        assert address.flat == flat
        assert address.entrance == entrance

    async def test_address_find_one_or_none(self, create_user, create_address):
        address = await AddressesDAO.find_one_or_none(user_id=create_user.id)

        assert address is not None
        assert address.user_id == create_user.id

    @pytest.mark.parametrize(
        "city, street, house, building, flat, entrance",
        [("SAINT_PETERSBURG", "Улица", 2, 2, 2, 2)],
    )
    async def test_address_update(
        self, create_user, create_address, city, street, house, building, flat, entrance
    ):
        address_updated = await AddressesDAO.update(
            create_address.id,
            city=city,
            street=street,
            house=house,
            building=building,
            flat=flat,
            entrance=entrance,
        )

        assert address_updated is not None
        assert address_updated.street == street
        assert address_updated.house == house
        assert address_updated.building == building
        assert address_updated.flat == flat
        assert address_updated.entrance == entrance
