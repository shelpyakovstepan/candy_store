# FIRSTPARTY
from app.addresses.models import Addresses  # noqa
from app.carts.models import Carts  # noqa
from app.cartsItems.models import CartsItems  # noqa
from app.database import SessionLocal
from app.favourites.models import Favourites  # noqa
from app.logger import logger
from app.orders.models import Orders  # noqa
from app.products.models import Products  # noqa
from app.purchases.models import Purchases  # noqa
from app.rabbitmq.broker import messages_queue, send_message
from app.users.dao import UsersDAO
from app.users.models import Users  # noqa

# Вынужденные noqa, так как без импортов моделей возникает ошибка с relationships.


async def add_phone_number(message):
    """
    Добавляет номер телефона в базу данных / отправляет сообщение в RabbitMQ о неудачном добавлении.

    Args:
        message: Сообщение с номером телефона.

    Returns:
        None
    """
    async with SessionLocal() as session:
        user = await UsersDAO.find_one_or_none(
            session=session, user_chat_id=message["chat_id"]
        )
        if not user:
            await send_message(
                message={
                    "chat_id": message["chat_id"],
                    "text": "Не удалось добавить номер телефона, так как Вы не зарегистрированы на сайте.\n"
                    "Пожалуйста, зарегистрируйтесь, прежде чем отправлять номер!",
                },
                queue=messages_queue,
            )
        else:
            try:
                await UsersDAO.update(
                    session=session,
                    model_id=user.id,
                    phone_number=message["phone_number"],
                )
                await session.commit()
            except Exception as e:
                logger.error(e, exc_info=True)
                await session.rollback()
                await send_message(
                    message={
                        "chat_id": user.user_chat_id,
                        "text": "Не удалось добавить номер телефона",
                    },
                    queue=messages_queue,
                )

        logger.info("Номер телефона обработан")
