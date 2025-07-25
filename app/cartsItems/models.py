# THIRDPARTY
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

# FIRSTPARTY
from app.database import Base


class CartsItems(Base):
    __tablename__ = "cartsItems"

    cart_id: Mapped[int] = mapped_column(ForeignKey("carts.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)

    cart = relationship("Carts", back_populates="carts_items")
    product = relationship("Products", back_populates="carts_items")

    def __str__(self):
        return f"{self.id}"
