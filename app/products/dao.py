# STDLIB
import math

# THIRDPARTY
from fastapi.encoders import jsonable_encoder
from pydantic import parse_obj_as
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

# FIRSTPARTY
from app.dao.base import BaseDao
from app.products.models import Products
from app.products.schemas import ProductsFilter, SProducts, SUpdateProduct


class ProductsDAO(BaseDao):
    model = Products

    @classmethod
    async def update_product(
        cls,
        session: AsyncSession,
        product_id: int,
        updated_product_data: SUpdateProduct,
    ):
        stored_product = select(Products).where(Products.id == product_id)
        stored_product = await session.execute(stored_product)
        stored_product = stored_product.scalar()

        stored_product_dict = parse_obj_as(SProducts, stored_product).model_dump()
        stored_product_model = SProducts(**stored_product_dict)
        update_data = updated_product_data.model_dump(exclude_defaults=True)
        updated_pr = stored_product_model.model_copy(update=update_data)
        updated_pr = jsonable_encoder(updated_pr)
        updated_pr["unit"] = updated_pr["unit"].upper()
        updated_pr["status"] = updated_pr["status"].upper()

        update_product_query = (
            update(Products)
            .where(Products.id == product_id)
            .values(**updated_pr)
            .returning(Products)
        )
        updated_product = await session.execute(update_product_query)

        return updated_product.scalar()

    @classmethod
    async def find_all_products(
        cls,
        session: AsyncSession,
        page: int,
        page_size: int,
        products_filter: ProductsFilter,
    ):
        offset = (page - 1) * page_size
        query_filter = products_filter.filter(
            select(Products).where(Products.status == "ACTIVE")
        )
        filtered_data = await session.execute(
            query_filter.offset(offset).limit(page_size)
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

    @classmethod
    async def find_all_product_categories(cls, session: AsyncSession):
        all_product_categories_query = (
            select(Products.category)
            .select_from(Products)
            .where(Products.status == "ACTIVE")
        )
        all_product_categories = await session.execute(all_product_categories_query)

        return list(set(all_product_categories.scalars().all()))
