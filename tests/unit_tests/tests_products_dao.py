# THIRDPARTY
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

# FIRSTPARTY
from app.products.dao import ProductsDAO, ProductsFilter


class TestProductsDAO:
    @pytest.mark.parametrize(
        "name, category, exists",
        [("Not_exists_name", "Торты", False), ("Торт обычный", "Торты", True)],
    )
    async def test_products_find_one_or_none(
        self,
        get_session: AsyncSession,
        create_user,
        create_product,
        name,
        category,
        exists,
    ):
        product = await ProductsDAO.find_one_or_none(
            session=get_session, name=name, category=category
        )

        if exists:
            assert product is not None
            assert product.name == name
            assert product.category == category
        else:
            assert not product

    @pytest.mark.parametrize("product_id, exists", [(333333, False), (222222, True)])
    async def test_products_find_by_id(
        self, get_session: AsyncSession, create_user, create_product, product_id, exists
    ):
        product = await ProductsDAO.find_by_id(get_session, product_id)
        if exists:
            assert product is not None
            assert product.id == product_id
        else:
            assert not product

    @pytest.mark.parametrize(
        "product_id, name, category, ingredients, unit, price, min_quantity, max_quantity, description, image_id",
        [
            (
                222222,
                "Торт обычный",
                "Торты",
                ["Шоколад"],
                "KILOGRAMS",
                2500,
                2,
                6,
                "description",
                1,
            )
        ],
    )
    async def test_products_update(
        self,
        get_session: AsyncSession,
        create_user,
        create_product,
        product_id,
        name,
        category,
        ingredients,
        unit,
        price,
        min_quantity,
        max_quantity,
        description,
        image_id,
    ):
        updated_product = await ProductsDAO.update(
            get_session,
            product_id,
            name=name,
            category=category,
            ingredients=ingredients,
            unit=unit,
            price=price,
            min_quantity=min_quantity,
            max_quantity=max_quantity,
            description=description,
            image_id=image_id,
        )

        assert updated_product is not None
        assert updated_product.name == name
        assert updated_product.category == category
        assert updated_product.ingredients == ingredients
        assert updated_product.price == price
        assert updated_product.min_quantity == min_quantity
        assert updated_product.max_quantity == max_quantity
        assert updated_product.description == description
        assert updated_product.image_id == image_id
        assert updated_product.id == product_id

    @pytest.mark.parametrize(
        "page, page_size, name__in, category__in, price__lte",
        [(1, 5, None, None, None)],
    )
    async def test_products_find_all(
        self,
        get_session: AsyncSession,
        create_user,
        create_product,
        page,
        page_size,
        name__in,
        category__in,
        price__lte,
    ):
        products_filter = ProductsFilter(
            name__in=name__in, category__in=category__in, price__lte=price__lte
        )

        products = await ProductsDAO.find_all_products(
            session=get_session,
            page=page,
            page_size=page_size,
            products_filter=products_filter,
        )

        assert products is not None

    async def test_products_delete(
        self, get_session: AsyncSession, create_user, create_product
    ):
        await ProductsDAO.delete(session=get_session, id=create_product.id)

        assert await ProductsDAO.find_by_id(get_session, create_product.id) is None
