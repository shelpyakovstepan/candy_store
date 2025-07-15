# STDLIB
import math
from typing import Optional

# THIRDPARTY
from fastapi.encoders import jsonable_encoder
from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import Field, parse_obj_as
from sqlalchemy import select, update

# FIRSTPARTY
from app.dao.base import BaseDao
from app.database import async_session_maker
from app.products.models import Products
from app.products.schemas import SProducts, SUpdateProduct


class ProductsFilter(Filter):
    name__in: Optional[list[str]] = Field(default=None)
    category__in: Optional[list[str]] = Field(default=None)
    price__lte: Optional[int] = Field(default=None)

    class Constants(Filter.Constants):
        model = Products


class ProductsDAO(BaseDao):
    model = Products

    @classmethod
    async def update_product(
        cls,
        product_id: int,
        updated_product_data: SUpdateProduct,
    ):
        async with async_session_maker() as session:
            stored_product = select(Products).where(Products.id == product_id)
            stored_product = await session.execute(stored_product)

            stored_product_dict = parse_obj_as(
                SProducts, stored_product.scalar()
            ).model_dump()
            stored_product_model = SProducts(**stored_product_dict)
            update_data = updated_product_data.model_dump(exclude_defaults=True)
            updated_pr = stored_product_model.model_copy(update=update_data)
            updated_pr = jsonable_encoder(updated_pr)
            updated_pr["unit"] = updated_pr["unit"].upper()

            update_product_query = (
                update(Products)
                .where(Products.id == product_id)
                .values(**updated_pr)
                .returning(Products)
            )
            updated_product = await session.execute(update_product_query)
            await session.commit()

            return updated_product.scalar()

    @classmethod
    async def find_all(  # pyright: ignore [reportIncompatibleMethodOverride]
        cls,
        page: int,
        page_size: int,
        products_filter: ProductsFilter,
    ):
        async with async_session_maker() as session:
            offset_min = (page - 1) * page_size
            query_filter = products_filter.filter(select(Products))
            filtered_data = await session.execute(
                query_filter.offset(offset_min).limit(page_size)
            )
            filtered_data = filtered_data.scalars().all()
            response = filtered_data + [  # pyright: ignore [reportOperatorIssue]
                {
                    "page": page,
                    "size": page_size,
                    "total": math.ceil(len(filtered_data) / page_size),
                }
            ]
            return response
