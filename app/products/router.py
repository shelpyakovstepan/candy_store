# THIRDPARTY
from fastapi import APIRouter, Query

# FIRSTPARTY
from app.exceptions import NotProductsException
from app.products.dao import ProductsDAO

router = APIRouter(
    prefix="/products",
    tags=["Товары"],
)


@router.get("/")
async def get_all_products(
    limit: int = Query(5, le=10, ge=5),
    offset: int = Query(0, ge=0),
):
    products = await ProductsDAO.find_all(limit=limit, offset=offset)

    if not products:
        raise NotProductsException

    return products
