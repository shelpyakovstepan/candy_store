# STDLIB
from datetime import date, time

# THIRDPARTY
from pydantic import BaseModel


class SOrders(BaseModel):
    id: int
    user_id: int
    created_at: date
    cart_id: int
    address: int
    date_receiving: date
    time_receiving: time
    receiving_method: str
    comment: str
    payment: str
    total_price: int
    status: str
