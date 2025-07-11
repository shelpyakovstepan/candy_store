# FIRSTPARTY
from app.dao.base import BaseDao
from app.products.models import Products


class ProductsDAO(BaseDao):
    model = Products
