# THIRDPARTY
from pydantic import BaseModel


class SAddresses(BaseModel):
    id: int
    user_id: int
    city: str
    street: str
    house: int
    building: int
    flat: int
    entrance: int


class SAddAndUpdateAddress(BaseModel):
    street: str
    house: int
    building: int
    flat: int
    entrance: int
