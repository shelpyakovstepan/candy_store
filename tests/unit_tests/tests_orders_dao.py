# STDLIB
from datetime import datetime

# THIRDPARTY
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

# FIRSTPARTY
from app.orders.dao import OrdersDAO, OrdersStatusFilter


class TestOrdersDAO:
    @pytest.mark.parametrize(
        "cart_id, date_receiving, time_receiving, receiving_method, payment, comment",
        [(222222, "2100-01-01", "12:00", "PICKUP", "CASH", "comment")],
    )
    async def test_orders_add(
        self,
        get_session: AsyncSession,
        create_address,
        create_product,
        create_cart,
        create_carts_item,
        cart_id,
        date_receiving,
        time_receiving,
        receiving_method,
        payment,
        comment,
    ):
        date_receiving = datetime.strptime(date_receiving, "%Y-%m-%d").date()
        time_receiving = datetime.strptime(time_receiving, "%H:%M").time()

        order = await OrdersDAO.add_order(
            session=get_session,
            user_id=create_address.user_id,
            cart_id=cart_id,
            address=create_address.id,
            date_receiving=date_receiving,
            time_receiving=time_receiving,
            receiving_method=receiving_method,
            payment=payment,
            comment=comment,
        )

        assert order is not None
        assert order.user_id == create_address.user_id
        assert order.cart_id == cart_id
        assert order.address == create_address.id
        assert order.date_receiving == date_receiving
        assert order.time_receiving == time_receiving
        assert order.comment == comment

    @pytest.mark.parametrize("user_id, exists", [(333333, False), (222222, True)])
    async def test_orders_find_all(
        self,
        get_session: AsyncSession,
        create_address,
        create_product,
        create_carts_item,
        create_order,
        user_id,
        exists,
    ):
        orders = await OrdersDAO.find_all(session=get_session, user_id=user_id)

        if exists:
            assert orders is not None
        else:
            assert not orders

    @pytest.mark.parametrize("order_id, exists", [(333333, False), (222222, True)])
    async def test_orders_find_by_id(
        self,
        get_session: AsyncSession,
        create_address,
        create_product,
        create_carts_item,
        create_order,
        order_id,
        exists,
    ):
        order = await OrdersDAO.find_by_id(session=get_session, model_id=order_id)

        if exists:
            assert order is not None
        else:
            assert not order

    @pytest.mark.parametrize(
        "user_id, cart_id, status, exists",
        [
            (333333, 333333, "WAITING", False),
            (222222, 222222, "WAITING", True),
        ],
    )
    async def test_orders_find_one_or_none(
        self,
        get_session: AsyncSession,
        create_address,
        create_product,
        create_carts_item,
        create_order,
        user_id,
        cart_id,
        status,
        exists,
    ):
        order = await OrdersDAO.find_one_or_none(
            session=get_session, user_id=user_id, cart_id=cart_id, status=status
        )

        if exists:
            assert order is not None
            assert order.user_id == create_address.user_id
            assert order.cart_id == create_carts_item.cart_id
        else:
            assert not order

    @pytest.mark.parametrize(
        "page, page_size, status",
        [
            (1, 5, "WAITING"),
        ],
    )
    async def test_find_all_users_orders(
        self,
        get_session: AsyncSession,
        create_address,
        create_product,
        create_carts_item,
        create_order,
        page,
        page_size,
        status,
    ):
        orders_status_filter = OrdersStatusFilter(status__in=status)

        assert (
            await OrdersDAO.find_all_users_orders(
                session=get_session,
                page=page,
                page_size=page_size,
                orders_status_filter=orders_status_filter,
            )
            is not None
        )

    async def test_orders_delete(
        self,
        get_session: AsyncSession,
        create_address,
        create_product,
        create_carts_item,
        create_order,
    ):
        await OrdersDAO.delete(session=get_session, id=create_order.id)

        assert await OrdersDAO.find_by_id(get_session, create_order.id) is None
