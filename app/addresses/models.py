# STDLIB
import enum

# THIRDPARTY
from sqlalchemy import ForeignKey
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship

# FIRSTPARTY
from app.database import Base


class CityEnum(enum.Enum):
    SAINT_PETERSBURG = "Saint-Petersburg"


class Addresses(Base):
    __tablename__ = "addresses"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    city: Mapped[CityEnum] = mapped_column(postgresql.ENUM(CityEnum), nullable=False)
    street: Mapped[str] = mapped_column(nullable=False)
    house: Mapped[int] = mapped_column(nullable=False)
    building: Mapped[int]
    flat: Mapped[int] = mapped_column(nullable=False)
    entrance: Mapped[int]
    status: Mapped[bool] = mapped_column(default=True, nullable=False)

    user = relationship("Users", back_populates="address")
    order = relationship("Orders", back_populates="address_")

    def __str__(self):
        return f"{self.street}"
