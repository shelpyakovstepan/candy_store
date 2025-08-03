# STDLIB
from datetime import date, datetime

# THIRDPARTY
import pytz
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

# FIRSTPARTY
from app.database import Base


class Purchases(Base):
    __tablename__ = "purchases"

    created_at: Mapped[date] = mapped_column(
        default=datetime.now(pytz.timezone("Europe/Moscow")).date(), nullable=False
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    price: Mapped[int]
    payment_type: Mapped[str]
    payment_id: Mapped[str] = mapped_column(unique=True)

    user = relationship("Users", back_populates="purchases")
    order = relationship("Orders", back_populates="purchases")

    def __repr__(self):
        return f"<Purchase(id={self.id}, user_id={self.user_id}, order_id={self.order_id}, date={self.created_at})>"
