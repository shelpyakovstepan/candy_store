# STDLIB
from typing import List, Literal

# THIRDPARTY
from fastapi import APIRouter, Depends

# FIRSTPARTY
from app.admin.dependencies import check_admin_status
from app.logger import logger
from app.products.dao import ProductsDAO

router = APIRouter(
    prefix="/admin",
    tags=["Для админов"],
    dependencies=[Depends(check_admin_status)],
)


@router.post("/product")
async def add_product(
    name: str,
    category: Literal["Торты", "Пряники"],
    ingredients: List[str],
    unit: Literal["PIECES", "KGS"],
    price: int,
    min_quantity: int,
    description: str,
    image_id: int,
):
    product = await ProductsDAO.add(
        name=name,
        category=category,
        ingredients=ingredients,
        unit=unit,
        price=price,
        min_quantity=min_quantity,
        description=description,
        image_id=image_id,
    )

    logger.debug("Продукт успешно добавлен")
    return product
