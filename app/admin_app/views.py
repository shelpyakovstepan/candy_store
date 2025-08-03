# THIRDPARTY
from sqladmin import ModelView

# FIRSTPARTY
from app.addresses.models import Addresses
from app.carts.models import Carts
from app.cartsItems.models import CartsItems
from app.favourites.models import Favourites
from app.orders.models import Orders
from app.products.models import Products
from app.purchases.models import Purchases
from app.users.models import Users


class UsersAdmin(ModelView, model=Users):
    column_list = [Users.id, Users.user_chat_id, Users.is_admin] + [
        Users.address,
        Users.order,
        Users.favourites,
    ]
    column_details_exclude_list = ["user_chat_id"]
    can_delete = False
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"


class AddressesAdmin(ModelView, model=Addresses):
    column_list = [c.name for c in Addresses.__table__.c] + [Addresses.user]
    name = "Адрес"
    name_plural = "Адреса"


class ProductsAdmin(ModelView, model=Products):
    column_list = [c.name for c in Products.__table__.c]
    name = "Товар"
    name_plural = "Товары"


class CartsAdmin(ModelView, model=Carts):
    column_list = [c.name for c in Carts.__table__.c] + [Carts.user, Carts.carts_items]
    name = "Корзина"
    name_plural = "Корзины"


class CartsItemsAdmin(ModelView, model=CartsItems):
    column_list = [c.name for c in CartsItems.__table__.c] + [
        CartsItems.cart,
        CartsItems.product,
    ]
    name = "Товар в корзине"
    name_plural = "Товары в корзине"


class OrdersAdmin(ModelView, model=Orders):
    column_list = [c.name for c in Orders.__table__.c] + [
        Orders.user,
        Orders.address_,
        Orders.cart,
        Orders.purchases,
    ]
    name = "Заказ"
    name_plural = "Заказы"


class FavouritesAdmin(ModelView, model=Favourites):
    column_list = [c.name for c in Favourites.__table__.c] + [
        Favourites.user,
        Favourites.product,
    ]
    name = "Товар в избранном"
    name_plural = "Избранное"


class PurchasesAdmin(ModelView, model=Purchases):
    column_list = [c.name for c in Purchases.__table__.c] + [
        Purchases.user,
        Purchases.order,
    ]
    name = "Покупка"
    name_plural = "Покупки"
