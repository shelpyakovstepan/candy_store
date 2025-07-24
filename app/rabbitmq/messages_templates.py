# FIRSTPARTY
from app.addresses.dao import AddressesDAO
from app.cartsItems.dao import CartsItemsDAO
from app.orders.models import (
    Orders,
    PaymentMethodEnum,
    ReceivingMethodEnum,
    StatusEnum,
)
from app.products.dao import ProductsDAO


async def convert_time_receiving_to_users_view(time_receiving):
    return str(time_receiving)[:5]


async def convert_receiving_method_to_users_view(receiving_method):
    if receiving_method == ReceivingMethodEnum.DELIVERY:
        return "Доставка"
    if receiving_method == ReceivingMethodEnum.PICKUP:
        return "Самовывоз"


async def convert_payment_to_users_view(payment):
    if payment == PaymentMethodEnum.NONCASH:
        return "Безналичный"
    if payment == PaymentMethodEnum.CASH:
        return "Наличные"


async def convert_status_to_users_view(status):
    if status == StatusEnum.WAITING:
        return "Ожидает оплаты"
    if status == StatusEnum.PREPARING:
        return "Готовится"
    if status == StatusEnum.READY:
        return "Готов"
    if status == StatusEnum.DELIVERY:
        return "Доставляется"
    if status == StatusEnum.COMPLETED:
        return "Выполнен"


async def create_orders_cart_items_text(cart_id):
    carts_items = await CartsItemsDAO.find_all(cart_id=cart_id)
    carts_items_text = ""
    number = 0
    for cart_item in carts_items:
        number += 1
        product = await ProductsDAO.find_by_id(cart_item.product_id)
        carts_items_text += (
            f"{number})\nТовар: {product.name}\nКоличество: {cart_item.quantity}\n\n"
        )
    return f"Позиции заказа:\n{carts_items_text}"


async def create_text_by_order_status(order):
    if order.status == StatusEnum.WAITING:
        return (
            "Пожалуйста, оплатите заказ на сайте, чтобы мы начали его готовить!\n"
            "Мы будем уведомлять вас об статусе заказа!"
        )
    if order.status == StatusEnum.PREPARING:
        return "Ваш заказ готовится!\nКогда он будет готов, мы уведомим вас!"
    if (
        order.status == StatusEnum.READY
        and order.receiving_method == ReceivingMethodEnum.DELIVERY
    ):
        return (
            "Ваш заказ готов!\nОжидайте доставку по указанному адресу, дате и времени!"
        )
    if (
        order.status == StatusEnum.READY
        and order.receiving_method == ReceivingMethodEnum.PICKUP
    ):
        return (
            "Ваш заказ готов!\n"
            "Заберите заказ по адресу самовывоза в указанную дату и время!"
        )
    if order.status == StatusEnum.DELIVERY:
        return "Ваш заказ передан в доставку!"
    if order.status == StatusEnum.COMPLETED:
        return "\n"


async def convert_address_to_users_view(order):
    if order.receiving_method == ReceivingMethodEnum.DELIVERY:
        address = await AddressesDAO.find_by_id(order.address)
        address_text = (
            f"Адрес:\n"
            f"Город: Санкт-Петербург\n"
            f"Улица: {address.street}\n"
            f"Дом: {address.house}\n"
            f"Корпус: {address.building}\n"
            f"Квартира: {address.flat}\n"
            f"Подъезд: {address.entrance}\n\n"
        )
    else:
        address_text = (
            "Адрес:\n"
            "Город: Санкт-Петербург\n"
            "Улица: Улица для самовывоза\n"
            "Дом: 1\n"
            "Корпус: 1\n"
            "Квартира: 1\n"
            "Подъезд: 1\n\n"
        )

    return address_text


async def admin_orders_text(order: Orders):
    admin_text_message = (
        f"Внимание! Пользователь с ID {order.user_id} создал заказ!\n"
        f"ID заказа: {order.id}\n"
        f"Состав заказа находится в корзине с ID: {order.cart_id}\n\n"
        f"{await create_orders_cart_items_text(order.cart_id)}"
        f"Заказ создан: {order.created_at}\n"
        f"Дата получения: {order.date_receiving}\n"
        f"Время получения: {await convert_time_receiving_to_users_view(order.time_receiving)}\n"
        f"Способ получения заказа: {await convert_receiving_method_to_users_view(order.receiving_method)}\n"
        f"Комментарий пользователя: {order.comment}\n"
        f"Способ оплаты: {await convert_payment_to_users_view(order.payment)}\n"
        f"Стоимость заказа: {order.total_price}\n"
        f"Статус заказа: {await convert_status_to_users_view(order.status)}\n\n"
        f"{await convert_address_to_users_view(order)}"
    )

    return admin_text_message


async def user_orders_text(order: Orders):
    user_text_message = (
        f"Вы создали заказ!\n\n"
        f"Уникальный номер заказа: {order.id}\n\n"
        f"{await create_orders_cart_items_text(order.cart_id)}"
        f"Заказ создан: {order.created_at}\n"
        f"Дата получения: {order.date_receiving}\n"
        f"Время получения: {await convert_time_receiving_to_users_view(order.time_receiving)}\n"
        f"Способ получения заказа: {await convert_receiving_method_to_users_view(order.receiving_method)}\n"
        f"Способ оплаты: {await convert_payment_to_users_view(order.payment)}\n"
        f"Стоимость заказа: {order.total_price}\n"
        f"Статус заказа: Ожидает оплаты\n\n"
        f"{await convert_address_to_users_view(order)}"
        f"Пожалуйста, оплатите заказ на сайте, чтобы мы начали его готовить!\n"
        f"Мы будем уведомлять вас об статусе заказа!"
    )

    return user_text_message


async def update_user_orders_text(order: Orders):
    update_user_orders_message = (
        f"Ваш заказ с уникальным номером {order.id} обновлён!\n\n"
        f"Статус заказа: {await convert_status_to_users_view(order.status)}\n\n"
        f"{await create_text_by_order_status(order)}"
    )

    return update_user_orders_message


# pyright: reportOptionalMemberAccess=false
# pyright: reportOptionalIterable=false
