# THIRDPARTY
from sqlalchemy.ext.asyncio import AsyncSession

# FIRSTPARTY
from app.favourites.dao import FavouritesDAO


class TestFavouritesDao:
    async def test_add_favourite(
        self, get_session: AsyncSession, create_user, create_product
    ):
        favourite = await FavouritesDAO.add(
            session=get_session, user_id=create_user.id, product_id=create_product.id
        )

        assert favourite is not None
        assert favourite.user_id == create_user.id
        assert favourite.product_id == create_product.id

    async def test_find_one_or_none_favourite(
        self, get_session: AsyncSession, create_user, create_product, create_favourite
    ):
        favourite = await FavouritesDAO.find_one_or_none(
            session=get_session, user_id=create_user.id, product_id=create_product.id
        )

        assert favourite is not None
        assert favourite.user_id == create_user.id
        assert favourite.product_id == create_product.id

    async def test_find_all_favourites(
        self, get_session: AsyncSession, create_user, create_product, create_favourite
    ):
        favourites = await FavouritesDAO.find_all(
            session=get_session, user_id=create_user.id
        )

        assert favourites is not None

    async def test_delete_favourite(
        self, get_session: AsyncSession, create_user, create_product, create_favourite
    ):
        await FavouritesDAO.delete(session=get_session, id=create_favourite.id)

        assert await FavouritesDAO.find_by_id(get_session, create_favourite.id) is None
