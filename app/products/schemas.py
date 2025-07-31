# STDLIB
from typing import List, Literal, Optional

# THIRDPARTY
from fastapi import Query
from fastapi_filter import FilterDepends
from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field

# FIRSTPARTY
from app.products.models import Products, StatusProductEnum, UnitEnum


class SProducts(BaseModel):
    id: int
    name: str
    category: str
    ingredients: List[str]
    unit: Literal[UnitEnum.PIECES, UnitEnum.KILOGRAMS]
    price: int
    min_quantity: int
    max_quantity: int
    description: str
    status: Literal[StatusProductEnum.ACTIVE, StatusProductEnum.INACTIVE]
    image_id: int

    class Config:
        from_attributes = True


class SUpdateProduct(BaseModel):
    id: int
    name: Optional[str] = None
    category: Optional[Literal["Торты", "Пряники"]] = None
    ingredients: Optional[List[str]] = []
    unit: Optional[Literal["PIECES", "KILOGRAMS"]] = None
    price: Optional[int] = None
    min_quantity: Optional[int] = None
    max_quantity: Optional[int] = None
    description: Optional[str] = None
    image_id: Optional[int] = None

    class Config:
        from_attributes = True


class SAddProduct(BaseModel):
    name: str
    category: Literal["Торты", "Пряники"]
    ingredients: List[str]
    unit: Literal["PIECES", "KILOGRAMS"]
    price: int
    min_quantity: int
    max_quantity: int
    description: str
    image_id: int


class SChangeProductStatus(BaseModel):
    product_id: int
    status: Literal["ACTIVE", "INACTIVE"]


class ProductsFilter(Filter):
    name__in: Optional[list[str]] = Field(default=None)
    category__in: Optional[list[str]] = Field(default=None)
    price__lte: Optional[int] = Field(default=None)

    class Constants(Filter.Constants):
        model = Products


class SGetProducts(BaseModel):
    page: int = Query(1, ge=1)
    page_size: int = Query(5, le=10, ge=5)
    products_filter: ProductsFilter = FilterDepends(ProductsFilter)
