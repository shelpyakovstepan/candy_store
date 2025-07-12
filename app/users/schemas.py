# STDLIB
import re

# THIRDPARTY
from pydantic import BaseModel, EmailStr, Field, field_validator


class SUsersRegister(BaseModel):
    email: EmailStr
    phone_number: str
    surname: str = Field(max_length=20)
    name: str = Field(max_length=20)
    password: str = Field(min_length=5, max_length=15)

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, values: str) -> str:
        if not re.match(r"^\+\d{11}$", values):
            raise ValueError(
                'Номер телефона должен начинаться с "+" и содержать 11 цифр'
            )
        return values


class SUsersLogin(BaseModel):
    email: EmailStr
    password: str


# class SUsers(BaseModel):
#    id: int
#    email: EmailStr
#    phone_number: str
#    surname: str
#    name: str
#    hashed_password: str
#    is_admin: bool
