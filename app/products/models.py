# STDLIB
import enum
from typing import List

# THIRDPARTY
from sqlalchemy import ARRAY, String, Text
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

# FIRSTPARTY
from app.database import Base


class UnitEnum(enum.Enum):
    PIECES = "pieces"
    KILOGRAMS = "kilograms"


class Products(Base):
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(nullable=False)
    category: Mapped[str] = mapped_column(nullable=False)
    ingredients: Mapped[List[str]] = mapped_column(ARRAY(String))
    unit: Mapped[UnitEnum] = mapped_column(postgresql.ENUM(UnitEnum), nullable=False)
    price: Mapped[int] = mapped_column(nullable=False)
    min_quantity: Mapped[int] = mapped_column(nullable=False)
    max_quantity: Mapped[int] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    image_id: Mapped[int]
