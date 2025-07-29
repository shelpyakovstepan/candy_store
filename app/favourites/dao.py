# FIRSTPARTY
from app.dao.base import BaseDao
from app.favourites.models import Favourites


class FavouritesDAO(BaseDao):
    model = Favourites
