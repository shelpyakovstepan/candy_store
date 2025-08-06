# STDLIB
from datetime import date, time
from typing import Literal, Optional

# THIRDPARTY
from fastapi import Query
from fastapi_filter import FilterDepends
from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field

# FIRSTPARTY
from app.orders.models import Orders


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

    class Config:
        from_attributes = True


class OrdersStatusFilter(Filter):
    status__in: Optional[
        list[Literal["WAITING", "PREPARING", "READY", "DELIVERY", "COMPLETED"]]
    ] = Field(
        default=None,
    )

    class Constants(Filter.Constants):
        model = Orders


class SGetAllOrders(BaseModel):
    page: int = Query(1, ge=1)
    page_size: int = Query(5, le=10, ge=5)
    orders_status_filter: OrdersStatusFilter = FilterDepends(OrdersStatusFilter)


class SChangeOrderStatus(BaseModel):
    order_id: int
    status: Literal["READY", "DELIVERY", "COMPLETED"]


class SCreateOrder(BaseModel):
    date_receiving: date
    time_receiving: time
    receiving_method: Literal["PICKUP", "DELIVERY"]
    comment: Optional[str] = Query("", max_length=100)
