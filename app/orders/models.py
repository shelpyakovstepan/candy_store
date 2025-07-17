# STDLIB
from datetime import date, datetime, time
import enum

# THIRDPARTY
import pytz
from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

# FIRSTPARTY
from app.database import Base


class ReceivingMethodEnum(enum.Enum):
    PICKUP = "pickup"
    DELIVERY = "delivery"


class StatusEnum(enum.Enum):
    WAITING = "waiting"
    PREPARING = "preparing"
    READY = "ready"
    DELIVERY = "delivered"
    COMPLETED = "completed"


class PaymentMethodEnum(enum.Enum):
    CASH = "cash"
    NONCASH = "non-cash"


class Orders(Base):
    __tablename__ = "orders"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[date] = mapped_column(
        default=datetime.now(pytz.timezone("Europe/Moscow")).date(), nullable=False
    )
    cart_id: Mapped[int] = mapped_column(ForeignKey("carts.id"), nullable=False)
    address: Mapped[int] = mapped_column(ForeignKey("addresses.id"))
    date_receiving: Mapped[date] = mapped_column(nullable=False)
    time_receiving: Mapped[time] = mapped_column(nullable=False)
    receiving_method: Mapped[ReceivingMethodEnum] = mapped_column(
        postgresql.ENUM(ReceivingMethodEnum), nullable=False
    )
    comment: Mapped[str] = mapped_column(Text)
    payment: Mapped[PaymentMethodEnum] = mapped_column(
        postgresql.ENUM(PaymentMethodEnum), nullable=False
    )
    total_price: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[StatusEnum] = mapped_column(
        postgresql.ENUM(StatusEnum), nullable=False
    )
