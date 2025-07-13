# STDLIB
from typing import List, Literal

# THIRDPARTY
from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from pydantic.v1 import parse_obj_as

# FIRSTPARTY
from app.admin.dependencies import check_admin_status
from app.exceptions import NotUserException
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
    unit: Literal["PIECES", "KGS"],
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

    logger.debug("Продукт успешно добавлен")
    return product  # pyright: ignore [reportReturnType]


@router.patch("/product/{product_id}")
async def update_product(
    product_id: int,
    updated_product_data: SUpdateProduct = Depends(),
) -> SProducts:
    stored_product = await ProductsDAO.find_one_or_none(id=product_id)
    stored_product_dict = parse_obj_as(SProducts, stored_product).model_dump()
    stored_product_model = SProducts(**stored_product_dict)
    update_data = updated_product_data.model_dump(exclude_defaults=True)
    updated_pr = stored_product_model.model_copy(update=update_data)
    updated_pr = jsonable_encoder(updated_pr)
    updated_pr["unit"] = updated_pr["unit"].upper()
    updated_product = await ProductsDAO.update(product_id, **updated_pr)

    logger.debug("Продукт успешно изменён")
    return updated_product  # pyright: ignore [reportReturnType]


@router.patch("/")
async def change_admin_status(user_id: int, admin_status: bool):
    """Изменяет статус админа пользователя."""
    user = await UserDAO.update(user_id, is_admin=admin_status)
    if not user:
        raise NotUserException

    return user  # pyright: ignore [reportReturnType]
