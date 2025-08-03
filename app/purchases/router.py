# THIRDPARTY
from fastapi import APIRouter
from fastapi.requests import Request
from starlette.exceptions import HTTPException
from starlette.responses import PlainTextResponse

# FIRSTPARTY
from app.config import settings
from app.database import DbSession
from app.logger import logger
from app.orders.dao import OrdersDAO
from app.orders.models import StatusEnum
from app.purchases.dao import PurchasesDAO
from app.purchases.utils import check_signature_result
from app.rabbitmq.base import send_message
from app.rabbitmq.messages_templates import (
    admin_orders_text,
    update_user_orders_text,
)
from app.users.dao import UsersDAO

router = APIRouter(
    prefix="/purchases",
    tags=["Покупки"],
)


@router.post("/result/")
async def robokassa_result(session: DbSession, request: Request) -> PlainTextResponse:
    """
    Обрабатывает запрос от Робокассы на ResultURL, изменяет статус заказа.

    Args:
        session: DbSession(AsyncSession) - Асинхронная сессия базы данных.
        request: HTTP-запрос.

    Returns:
        Текстовый ответ с результатами проверки.
    """
    logger.info("Получен ответ от Робокассы!")
    params = await request.form()
    if not params:
        raise HTTPException(status_code=400)

    signature = params.get("SignatureValue")
    out_sum = params.get("OutSum")
    inv_id = params.get("InvId")
    user_id = params.get("Shp_user_id")
    user_telegram_id = params.get("Shp_user_telegram_id")
    order_id = params.get("Shp_order_id")

    if check_signature_result(
        out_sum=out_sum,
        inv_id=inv_id,
        received_signature=signature,
        password=settings.MRH_PASS_2,
        user_id=user_id,
        user_telegram_id=user_telegram_id,
        order_id=order_id,
    ):
        result = f"OK{inv_id}"
        logger.info(f"Успешная проверка подписи для InvId: {inv_id}")

        payment_data = {
            "user_id": int(user_id),
            "payment_id": signature,
            "price": int(out_sum),
            "order_id": int(order_id),
            "payment_type": "robocassa",
        }

        pay_order = await OrdersDAO.find_by_id(session, payment_data["order_id"])

        if pay_order and pay_order.status != StatusEnum.WAITING:
            return PlainTextResponse(result)

        await PurchasesDAO.add(session=session, **payment_data)

        pay_order = await OrdersDAO.update(
            session, payment_data["order_id"], status="PREPARING"
        )
        user = await UsersDAO.find_by_id(session, payment_data["user_id"])

        await send_message(
            await admin_orders_text(session, order=pay_order), "admin-queue"
        )  # pyright: ignore [reportArgumentType]
        await send_message(
            {
                "chat_id": user.user_chat_id,  # pyright: ignore [reportOptionalMemberAccess]
                "text": await update_user_orders_text(order=pay_order),  # pyright: ignore [reportArgumentType]
            },
            "messages-queue",
        )

    else:
        result = "bad sign"
        logger.warn(f"Неверная подпись для InvId: {inv_id}")

    logger.info(f"Ответ: {result}")
    return PlainTextResponse(result)

# pyright: reportArgumentType=false