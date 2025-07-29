# STDLIB
from typing import List

# THIRDPARTY
from fastapi import APIRouter, Depends

# FIRSTPARTY
from app.exceptions import (
    FavouriteAlreadyExistsException,
    NotProductsException,
    YouDoNotHaveFavouriteWithThisIdException,
)
from app.favourites.dao import FavouritesDAO
from app.favourites.schemas import SFavourite
from app.products.dao import ProductsDAO
from app.users.dependencies import get_current_user
from app.users.models import Users

router = APIRouter(prefix="/favourites", tags=["Избранное"])


@router.post("/{product_id}")
async def add_favourite(
    product_id: int, user: Users = Depends(get_current_user)
) -> SFavourite:
    product = await ProductsDAO.find_one_or_none(id=product_id, status="ACTIVE")
    if not product:
        raise NotProductsException

    favourite = await FavouritesDAO.find_one_or_none(
        user_id=user.id, product_id=product_id
    )
    if favourite:
        raise FavouriteAlreadyExistsException

    favourite = await FavouritesDAO.add(user_id=user.id, product_id=product_id)

    return favourite


@router.get("")
async def get_favourites(user: Users = Depends(get_current_user)) -> List[SFavourite]:
    favourites = await FavouritesDAO.find_all(user_id=user.id)

    return favourites


@router.delete("/")
async def delete_favourite(
    favourite_id: int, user: Users = Depends(get_current_user)
) -> None:
    if not await FavouritesDAO.find_one_or_none(id=favourite_id, user_id=user.id):
        raise YouDoNotHaveFavouriteWithThisIdException

    await FavouritesDAO.delete(id=favourite_id)
