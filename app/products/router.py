# STDLIB
from typing import List

# THIRDPARTY
from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache

# FIRSTPARTY
from app.database import DbSession
from app.exceptions import NotProductsException
from app.products.dao import ProductsDAO
from app.products.schemas import SGetProducts, SProducts, SProductsCategories

router = APIRouter(
    prefix="/products",
    tags=["Товары"],
)


@router.get("/")
@cache(expire=30)
async def get_products(
    session: DbSession, find_product_data: SGetProducts = Depends()
) -> List[SProducts]:
    """
    Отдаёт все товары с возможностью фильтрации.

    Args:
        session: DbSession(AsyncSession) - Асинхронная сессия базы данных.
        find_product_data: Pydantic модель SGetProducts, содержащая данные для извлечения товаров.

    Returns:
        products: Список экземпляров модели Products, представляющий все товары.
    """
    products = await ProductsDAO.find_all_products(
        session,
        page=find_product_data.page,
        page_size=find_product_data.page_size,
        products_filter=find_product_data.products_filter,
    )

    if not products:
        raise NotProductsException

    return products


@router.get("/{product_id}")
async def get_product_by_id(session: DbSession, product_id: int) -> SProducts:
    """
    Отдаёт товар по ID.

    Args:
        session: DbSession(AsyncSession) - Асинхронная сессия базы данных.
        product_id: ID товара, который должен быть получен.

    Returns:
         product: Экземпляр модели Products, представляющий товар с указанным ID.
    """
    product = await ProductsDAO.find_one_or_none(
        session, id=product_id, status="ACTIVE"
    )
    if not product:
        raise NotProductsException
    return product


@router.get("//categories")
@cache(expire=30)
async def get_all_categories(session: DbSession) -> List[SProductsCategories]:
    """
    Отдаёт все категории товаров.

    Args:
        session: DbSession(AsyncSession) - Асинхронная сессия базы данных.

    Returns:
        categories: Список всех категорий товаров.
    """
    categories = await ProductsDAO.find_all_product_categories(session)

    return categories
