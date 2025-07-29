# THIRDPARTY
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

# FIRSTPARTY
from app.database import Base


class Favourites(Base):
    __tablename__ = "favourites"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)

    user = relationship("Users", back_populates="favourites")
    product = relationship("Products", back_populates="favourites")

    def __str__(self):
        return f"{self.id}"
