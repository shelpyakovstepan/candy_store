# STDLIB
from typing import List

# THIRDPARTY
from fastapi import APIRouter, Query
from fastapi_cache.decorator import cache
from fastapi_filter import FilterDepends

# FIRSTPARTY
from app.exceptions import NotProductsException
from app.products.dao import ProductsDAO, ProductsFilter
from app.products.schemas import SProducts

router = APIRouter(
    prefix="/products",
    tags=["Товары"],
)


@router.get("/")
@cache(expire=60)
async def get_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(5, le=10, ge=5),
    products_filter: ProductsFilter = FilterDepends(ProductsFilter),
) -> List[SProducts]:
    products = await ProductsDAO.find_all(
        page=page, page_size=page_size, products_filter=products_filter
    )

    if not products:
        raise NotProductsException

    return products


@router.get("/{product_id}")
async def get_product_by_id(product_id: int) -> SProducts:
    product = await ProductsDAO.find_by_id(product_id)
    if not product:
        raise NotProductsException
    return product
