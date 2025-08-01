# STDLIB
import shutil

# THIRDPARTY
from fastapi import APIRouter, Depends, UploadFile

# FIRSTPARTY
from app.admin.dependencies import check_admin_status
from app.carts.dao import CartsDAO
from app.cartsItems.dao import CartsItemsDAO
from app.database import DbSession
from app.exceptions import (
    NotOrdersException,
    NotProductsException,
    NotUserException,
    ProductAlreadyExistsException,
)
from app.favourites.dao import FavouritesDAO
from app.logger import logger
from app.orders.dao import OrdersDAO
from app.orders.schemas import SChangeOrderStatus, SGetAllOrders, SOrders
from app.products.dao import ProductsDAO
from app.products.schemas import (
    SAddProduct,
    SChangeProductStatus,
    SProducts,
    SUpdateProduct,
)
from app.rabbitmq.base import send_message
from app.rabbitmq.messages_templates import update_user_orders_text
from app.users.dao import UsersDAO
from app.users.schemas import SChangeAdminStatus, SUsers

router = APIRouter(
    prefix="/admins",
    tags=["Для админов"],
    dependencies=[Depends(check_admin_status)],
)


@router.post("/product")
async def add_product(
    session: DbSession, product_data: SAddProduct = Depends()
) -> SProducts:
    """
    Создаёт новый продукт.

    Args:
        session: DbSession(AsyncSession) - Асинхронная сессия базы данных.
        product_data: Pydantic модель SAddProduct, содержащая данные для добавления нового товара.

    Returns:
        product: Экземпляр модели Products, представляющий созданный товар.
    """
    product = await ProductsDAO.find_one_or_none(
        session, name=product_data.name, category=product_data.category
    )
    if product:
        raise ProductAlreadyExistsException

    product = await ProductsDAO.add(
        session,
        name=product_data.name,
        category=product_data.category,
        ingredients=product_data.ingredients,
        unit=product_data.unit,
        price=product_data.price,
        min_quantity=product_data.min_quantity,
        max_quantity=product_data.max_quantity,
        description=product_data.description,
        image_id=product_data.image_id,
    )

    logger.info("Продукт успешно добавлен")
    return product  # pyright: ignore [reportReturnType]


@router.patch("/product/{product_id}")
async def update_product(
    session: DbSession,
    updated_product_data: SUpdateProduct = Depends(),
):
    """
     Изменяет существующий товар.

    Args:
         session: DbSession(AsyncSession) - Асинхронная сессия базы данных.
         updated_product_data: Pydantic модель SUpdateProduct, содержащая данные для изменения товара.

     Returns:
         updated_product: Экземпляр модели Products, представляющий изменённый товар.
    """
    stored_product = await ProductsDAO.find_by_id(session, updated_product_data.id)
    if not stored_product:
        raise NotProductsException

    updated_product = await ProductsDAO.update_product(
        session, updated_product_data.id, updated_product_data
    )

    logger.info("Продукт успешно изменён")
    return updated_product  # pyright: ignore [reportReturnType]


@router.patch("/")
async def change_product_status(
    session: DbSession, change_product_status_data: SChangeProductStatus = Depends()
):
    """
    Изменяет статус существующего товар.

    Args:
        session: DbSession(AsyncSession) - Асинхронная сессия базы данных.
        change_product_status_data: Pydantic модель SChangeProductStatus, содержащая данные для изменения статуса товара.

    Returns:
        updated_product: Экземпляр модели Products, представляющий товар с изменённым статусом.
    """
    stored_product = await ProductsDAO.find_by_id(
        session, change_product_status_data.product_id
    )
    if not stored_product:
        raise NotProductsException

    if change_product_status_data.status == "INACTIVE":
        all_active_carts = await CartsDAO.find_all(session, status="ACTIVE")
        if all_active_carts:
            for active_cart in all_active_carts:
                await CartsItemsDAO.delete(
                    session,
                    product_id=change_product_status_data.product_id,
                    cart_id=active_cart.id,
                )
        await FavouritesDAO.delete(
            session, product_id=change_product_status_data.product_id
        )

    updated_product = await ProductsDAO.update(
        session,
        change_product_status_data.product_id,
        status=change_product_status_data.status,
    )
    logger.info("Статус продукта успешно изменён")
    return updated_product


@router.get("/orders")
async def get_all_users_orders(
    session: DbSession,
    get_all_orders_data: SGetAllOrders = Depends(),
):
    """
    Отдаёт все заказы пользователей с возможностью фильтрации.

    Args:
        session: DbSession(AsyncSession) - Асинхронная сессия базы данных.
        get_all_orders_data: Pydantic модель SGetAllOrders, содержащая данные для извлечения заказов.

    Returns:
        orders: Список экземпляров модели Orders, представляющий полученные заказы.
    """
    orders = await OrdersDAO.find_all_users_orders(
        session,
        page=get_all_orders_data.page,
        page_size=get_all_orders_data.page_size,
        orders_status_filter=get_all_orders_data.orders_status_filter,
    )

    if not orders:
        raise NotOrdersException

    return orders


@router.patch("/update/{order_id}")
async def change_order_status(
    session: DbSession, change_order_status_data: SChangeOrderStatus = Depends()
) -> SOrders:
    """
    Изменяет статус существующего заказа и отправляет уведомление пользователю.

    Args:
        session: DbSession(AsyncSession) - Асинхронная сессия базы данных.
        change_order_status_data: Pydantic модель SChangeOrderStatus, содержащая данные для изменения статуса заказа.

    Returns:
        order: Экземпляр модели Orders, представляющий заказ с изменённым статусом.
    """
    order = await OrdersDAO.find_by_id(session, change_order_status_data.order_id)
    if not order:
        raise NotOrdersException

    user = await UsersDAO.find_by_id(session, order.user_id)

    updated_order = await OrdersDAO.update(
        session,
        change_order_status_data.order_id,
        status=change_order_status_data.status,
    )
    await send_message(
        {
            "chat_id": user.user_chat_id,  # pyright: ignore [reportOptionalMemberAccess]
            "text": await update_user_orders_text(order=updated_order),  # pyright: ignore [reportArgumentType]
        },
        "messages-queue",
    )
    return order


@router.patch("//")
async def change_admin_status(
    session: DbSession, change_admin_status_data: SChangeAdminStatus = Depends()
) -> SUsers:
    """
    Изменяет статус админа пользователя.

    Args:
        session: DbSession(AsyncSession) - Асинхронная сессия базы данных.
        change_admin_status_data: Pydantic модель SChangeAdminStatus, содержащая данные для изменения статуса админа пользователя.

    Returns:
        user: Экземпляр модели Users, представляющий пользователя с изменённым статусом админа.
    """
    user = await UsersDAO.update(
        session,
        change_admin_status_data.user_id,
        is_admin=change_admin_status_data.admin_status,
    )
    if not user:
        raise NotUserException

    return user  # pyright: ignore [reportReturnType]


@router.post("/images/products")
async def upload_product_image(name: int, file: UploadFile):
    """
    Добавляет фото для продукта.

    Args:
        name: Имя, под которым сохранится фото.
        file: Файл с фото, которое должно быть сохранено.

    Returns:
        None
    """
    with open(f"app/static/images/{name}.webp", "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
