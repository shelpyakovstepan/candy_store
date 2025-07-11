# THIRDPARTY
from pydantic import BaseModel, EmailStr, Field


class SUsersRegister(BaseModel):
    email: EmailStr
    phone_number: str = Field(min_length=11, max_length=12)
    surname: str = Field(max_length=20)
    name: str = Field(max_length=20)
    password: str = Field(min_length=5, max_length=15)


class SUsersLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=5, max_length=15)


# class SUsers(BaseModel):
#    id: int
#    email: EmailStr
#    phone_number: str
#    surname: str
#    name: str
#    hashed_password: str
#    is_admin: bool
