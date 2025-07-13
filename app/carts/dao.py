# FIRSTPARTY
from app.carts.models import Carts
from app.dao.base import BaseDao


class CartsDAO(BaseDao):
    model = Carts
