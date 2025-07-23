# STDLIB
import enum

# THIRDPARTY
from sqlalchemy import ForeignKey
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

# FIRSTPARTY
from app.database import Base


class StatusCartEnum(enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class Carts(Base):
    __tablename__ = "carts"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    total_price: Mapped[int] = mapped_column(default=0)
    status: Mapped[StatusCartEnum] = mapped_column(
        postgresql.ENUM(StatusCartEnum), default=StatusCartEnum.ACTIVE, nullable=False
    )
