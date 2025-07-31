# THIRDPARTY
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

# FIRSTPARTY
from app.carts.models import Carts
from app.cartsItems.models import CartsItems
from app.dao.base import BaseDao
from app.products.models import Products


class CartsItemsDAO(BaseDao):
    model = CartsItems

    @classmethod
    async def add_cart_item(
        cls,
        session: AsyncSession,
        cart_id: int,
        product_id: int,
        quantity: int,
    ):
        add_new_carts_item_query = (
            insert(CartsItems)
            .values(cart_id=cart_id, product_id=product_id, quantity=quantity)
            .returning(CartsItems)
        )
        add_new_carts_item = await session.execute(add_new_carts_item_query)
        add_new_carts_item = add_new_carts_item.scalar()

        price = (
            select(Products.price)
            .select_from(Products)
            .where(Products.id == product_id)
        )
        price = await session.execute(price)
        update_cart_total_price = (
            update(Carts)
            .where(Carts.id == cart_id)
            .values(total_price=(Carts.total_price + (price.scalar() * quantity)))
            .returning(Carts.total_price)
        )
        await session.execute(update_cart_total_price)

        return add_new_carts_item

    @classmethod
    async def update_carts_item(
        cls,
        session: AsyncSession,
        cart_item_id: int,
        action: str,
        quantity: int,
    ):
        if action == "reduce":
            update_cart_item_quantity_query = (
                update(CartsItems)
                .where(CartsItems.id == cart_item_id)
                .values(quantity=CartsItems.quantity - quantity)
                .returning(CartsItems)
            )
            update_cart_item_quantity = await session.execute(
                update_cart_item_quantity_query
            )
            await session.commit()
            update_cart_item_quantity = update_cart_item_quantity.scalar()

            price = (
                select(Products.price)
                .select_from(Products)
                .where(Products.id == update_cart_item_quantity.product_id)
            )
            price = await session.execute(price)
            update_cart_total_price = (
                update(Carts)
                .where(Carts.id == update_cart_item_quantity.cart_id)
                .values(total_price=(Carts.total_price - (price.scalar() * quantity)))
                .returning(Carts.total_price)
            )

        else:
            update_cart_item_quantity_query = (
                update(CartsItems)
                .where(CartsItems.id == cart_item_id)
                .values(quantity=CartsItems.quantity + quantity)
                .returning(CartsItems)
            )
            update_cart_item_quantity = await session.execute(
                update_cart_item_quantity_query
            )
            await session.commit()
            update_cart_item_quantity = update_cart_item_quantity.scalar()

            price = (
                select(Products.price)
                .select_from(Products)
                .where(Products.id == update_cart_item_quantity.product_id)
            )
            price = await session.execute(price)
            update_cart_total_price = (
                update(Carts)
                .where(Carts.id == update_cart_item_quantity.cart_id)
                .values(total_price=(Carts.total_price + (price.scalar() * quantity)))
                .returning(Carts.total_price)
            )

        await session.execute(update_cart_total_price)

        return update_cart_item_quantity

    @classmethod
    async def delete_carts_item(
        cls,
        session: AsyncSession,
        cart_item_id: int,
    ):
        delete_cart_item_query = (
            delete(CartsItems)
            .where(CartsItems.id == cart_item_id)
            .returning(CartsItems)
        )
        delete_cart_item = await session.execute(delete_cart_item_query)
        delete_cart_item = delete_cart_item.scalar()

        price = (
            select(Products.price)
            .select_from(Products)
            .where(Products.id == delete_cart_item.product_id)
        )
        price = await session.execute(price)
        update_cart_total_price = (
            update(Carts)
            .where(Carts.id == delete_cart_item.cart_id)
            .values(
                total_price=(
                    Carts.total_price - (price.scalar() * delete_cart_item.quantity)
                )
            )
            .returning(Carts.total_price)
        )
        await session.execute(update_cart_total_price)


# pyright: reportOptionalMemberAccess=false
# pyright: reportOptionalOperand=false
# pyright: reportPossiblyUnboundVariable=false
# pyright: reportAttributeAccessIssue=false
