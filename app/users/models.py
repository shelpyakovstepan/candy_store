# THIRDPARTY
from sqlalchemy import BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

# FIRSTPARTY
from app.database import Base


class Users(Base):
    __tablename__ = "users"

    user_chat_id: Mapped[int] = mapped_column(BIGINT, nullable=False, unique=True)
    is_admin: Mapped[bool] = mapped_column(nullable=False, default=False)

    address = relationship("Addresses", back_populates="user")
    cart = relationship("Carts", back_populates="user")
    order = relationship("Orders", back_populates="user")
    favourites = relationship("Favourites", back_populates="user")

    def __str__(self):
        return f"{self.id}"
