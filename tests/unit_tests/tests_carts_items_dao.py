# THIRDPARTY
import pytest

# FIRSTPARTY
from app.cartsItems.dao import CartsItemsDAO


class TestCartsItemsDAO:
    async def test_carts_item_add(self, create_cart, create_product):
        carts_item = await CartsItemsDAO.add(
            cart_id=create_cart.id, product_id=create_product.id, quantity=5
        )

        assert carts_item is not None
        assert carts_item.cart_id == create_cart.id
        assert carts_item.product_id == create_product.id
        assert carts_item.quantity == 5

    async def test_carts_item_find_all(
        self, create_cart, create_product, create_carts_item
    ):
        carts_items = await CartsItemsDAO.find_all(cart_id=create_cart.id)
        assert carts_items is not None

    @pytest.mark.parametrize(
        "cart_id, product_id, exists",
        [
            (222222, 222222, True),
            (333333, 333333, False),
        ],
    )
    async def test_carts_item_find_one_or_none(
        self,
        create_cart,
        create_product,
        create_carts_item,
        cart_id,
        product_id,
        exists,
    ):
        carts_item = await CartsItemsDAO.find_one_or_none(
            cart_id=cart_id, product_id=product_id
        )

        if exists:
            assert carts_item is not None
            assert carts_item.cart_id == cart_id
            assert carts_item.product_id == product_id
        else:
            assert carts_item is None

    @pytest.mark.parametrize(
        "action, quantity",
        [
            ("increase", 2),
            ("reduce", 1),
        ],
    )
    async def test_update_carts_item(
        self, create_cart, create_product, create_carts_item, action, quantity
    ):
        updated_carts_item = await CartsItemsDAO.update_carts_item(
            cart_item_id=create_carts_item.id, action=action, quantity=quantity
        )

        assert updated_carts_item is not None

    async def test_carts_item_delete(
        self, create_cart, create_product, create_carts_item
    ):
        await CartsItemsDAO.delete_carts_item(cart_item_id=create_carts_item.id)

        assert await CartsItemsDAO.find_by_id(create_cart.id) is None
