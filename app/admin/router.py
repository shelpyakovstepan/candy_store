# STDLIB
from typing import List, Literal

# THIRDPARTY
from fastapi import APIRouter, Depends

# FIRSTPARTY
from app.admin.dependencies import check_admin_status
from app.exceptions import NotProductsException, NotUserException
from app.logger import logger
from app.products.dao import ProductsDAO
from app.products.schemas import SProducts, SUpdateProduct
from app.users.dao import UserDAO

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
    unit: Literal["PIECES", "KILOGRAMS"],
    price: int,
    min_quantity: int,
    description: str,
    image_id: int,
) -> SProducts:
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

    logger.info("Продукт успешно добавлен")
    return product  # pyright: ignore [reportReturnType]


@router.patch("/product/{product_id}")
async def update_product(
    product_id: int,
    updated_product_data: SUpdateProduct = Depends(),
) -> SProducts:
    stored_product = await ProductsDAO.find_one_or_none(id=product_id)
    if not stored_product:
        raise NotProductsException

    updated_product = await ProductsDAO.update_product(product_id, updated_product_data)

    logger.info("Продукт успешно изменён")
    return updated_product  # pyright: ignore [reportReturnType]


@router.delete("/")
async def delete_product(product_id: int):
    stored_product = await ProductsDAO.find_one_or_none(id=product_id)
    if not stored_product:
        raise NotProductsException

    logger.info("Продукт успешно удалён")
    await ProductsDAO.delete(id=product_id)


@router.patch("/")
async def change_admin_status(user_id: int, admin_status: bool):
    """Изменяет статус админа пользователя."""
    user = await UserDAO.update(user_id, is_admin=admin_status)
    if not user:
        raise NotUserException

    return user  # pyright: ignore [reportReturnType]
