# STDLIB
from typing import List, Literal, Optional

# THIRDPARTY
from pydantic import BaseModel

# FIRSTPARTY
from app.products.models import UnitEnum


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
    image_id: int

    class Config:
        from_attributes = True


class SUpdateProduct(BaseModel):
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
