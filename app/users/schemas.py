# STDLIB
import re

# THIRDPARTY
from pydantic import BaseModel, field_validator
from starlette.exceptions import HTTPException


class SUsers(BaseModel):
    id: int
    user_chat_id: int
    is_admin: int


class SUsersWithPhoneNumber(BaseModel):
    id: int
    user_chat_id: int
    is_admin: int
    phone_number: str


class SChangeAdminStatus(BaseModel):
    user_id: int
    admin_status: bool


class SPhoneNumber(BaseModel):
    phone_number: str

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, values: str) -> str:
        if not re.match(r"^\+\d{11}$", values):
            raise HTTPException(
                status_code=422,
                detail='Номер телефона должен начинаться с "+" и содержать 11 цифр',
            )
        return values
