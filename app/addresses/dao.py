# FIRSTPARTY
from app.addresses.models import Addresses
from app.dao.base import BaseDao


class AddressesDAO(BaseDao):
    model = Addresses
