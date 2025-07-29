# THIRDPARTY
from pydantic import BaseModel


class SFavourite(BaseModel):
    id: int
    user_id: int
    product_id: int
