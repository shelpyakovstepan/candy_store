# THIRDPARTY
from sqlalchemy import BIGINT
from sqlalchemy.orm import Mapped, mapped_column

# FIRSTPARTY
from app.database import Base


class Users(Base):
    __tablename__ = "users"

    user_chat_id: Mapped[int] = mapped_column(BIGINT, nullable=False, unique=True)
    is_admin: Mapped[bool] = mapped_column(nullable=False, default=False)
