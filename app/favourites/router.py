# STDLIB
from typing import List

# THIRDPARTY
from fastapi import APIRouter, Depends

# FIRSTPARTY
from app.database import DbSession
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
    session: DbSession, product_id: int, user: Users = Depends(get_current_user)
) -> SFavourite:
    """
    Добавляет товар в избранное.

    Args:
        session: DbSession(AsyncSession) - Асинхронная сессия базы данных.
        product_id: ID товара, который должен быть добавлен в избранное.
        user: Экземпляр модели Users, представляющий текущего пользователя, полученный через зависимость get_current_user().

    Returns:
        favourite: Экземпляр модели Favourites, представляющий товар в избранном.
    """
    product = await ProductsDAO.find_one_or_none(
        session, id=product_id, status="ACTIVE"
    )
    if not product:
        raise NotProductsException

    favourite = await FavouritesDAO.find_one_or_none(
        session, user_id=user.id, product_id=product_id
    )
    if favourite:
        raise FavouriteAlreadyExistsException

    favourite = await FavouritesDAO.add(session, user_id=user.id, product_id=product_id)

    return favourite


@router.get("")
async def get_favourites(
    session: DbSession, user: Users = Depends(get_current_user)
) -> List[SFavourite]:
    """
    Отдаёт все товары из избранного.

    Args:
        session: DbSession(AsyncSession) - Асинхронная сессия базы данных.
        user: Экземпляр модели Users, представляющий текущего пользователя, полученный через зависимость get_current_user().

    Returns:
        favourites: Список экземпляров модели Favourites, представляющий все товары в избранном пользователя.
    """
    favourites = await FavouritesDAO.find_all(session, user_id=user.id)

    return favourites


@router.delete("/")
async def delete_favourite(
    session: DbSession, favourite_id: int, user: Users = Depends(get_current_user)
) -> None:
    """
    Удаляет товар из избранного.

    Args:
        session: DbSession(AsyncSession) - Асинхронная сессия базы данных.
        favourite_id: ID товара в избранном, который должен быть удалён.
        user: Экземпляр модели Users, представляющий текущего пользователя, полученный через зависимость get_current_user().

    Returns:
        None
    """
    if not await FavouritesDAO.find_one_or_none(
        session, id=favourite_id, user_id=user.id
    ):
        raise YouDoNotHaveFavouriteWithThisIdException

    await FavouritesDAO.delete(session, id=favourite_id)
