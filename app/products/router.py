# THIRDPARTY
from fastapi import APIRouter, Query
from fastapi_filter import FilterDepends

# FIRSTPARTY
from app.exceptions import NotProductsException
from app.products.dao import ProductsDAO, ProductsFilter

router = APIRouter(
    prefix="/products",
    tags=["Товары"],
)


@router.get("/")
async def get_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(5, le=10, ge=5),
    products_filter: ProductsFilter = FilterDepends(ProductsFilter),
):
    products = await ProductsDAO.find_all(
        page=page, page_size=page_size, products_filter=products_filter
    )

    if not products:
        raise NotProductsException

    return products
