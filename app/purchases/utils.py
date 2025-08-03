# STDLIB
import hashlib
from urllib import parse

# FIRSTPARTY
from app.config import settings


def calculate_signature(
    login, cost, inv_id, password, user_id, user_telegram_id, order_id, is_result=False
):
    """Формирует цифровую подпись, которая подтверждает подлинность запроса."""
    if is_result:
        base_string = f"{cost}:{inv_id}:{password}"
    else:
        base_string = f"{login}:{cost}:{inv_id}:{password}"

    additional_params = {
        "Shp_user_id": user_id,
        "Shp_user_telegram_id": user_telegram_id,
        "Shp_order_id": order_id,
    }
    for key, value in sorted(additional_params.items()):
        base_string += f":{key}={value}"

    return hashlib.md5(base_string.encode("utf-8")).hexdigest()


def generate_payment_link(
    cost: float,
    number: int,
    description: str,
    user_id: int,
    user_telegram_id: int,
    order_id: int,
    is_test=1,
    robokassa_payment_url="https://auth.robokassa.ru/Merchant/Index.aspx",
) -> str:
    """
    Генерирует ссылку для оплаты через Robokassa с обязательными параметрами.

    Args:
        cost: Стоимость заказа.
        number: Номер заказа.
        description: Описание заказа.
        user_id: ID пользователя.
        user_telegram_id: Telegram-чат ID пользователя.
        order_id: ID заказа.
        is_test: Флаг тестового режима (1 - тест, 0 - боевой режим).
        robokassa_payment_url: URL для оплаты Robokassa.

    Returns:
        Ссылка на страницу оплаты.
    """
    signature = calculate_signature(
        settings.MRH_LOGIN,
        cost,
        number,
        settings.MRH_PASS_1,
        user_id,
        user_telegram_id,
        order_id,
    )

    data = {
        "MerchantLogin": settings.MRH_LOGIN,
        "OutSum": cost,
        "InvId": number,
        "Description": description,
        "SignatureValue": signature,
        "IsTest": is_test,
        "Shp_user_id": user_id,
        "Shp_user_telegram_id": user_telegram_id,
        "Shp_order_id": order_id,
    }

    return f"{robokassa_payment_url}?{parse.urlencode(data)}"


def check_signature_result(
    out_sum, inv_id, received_signature, password, user_id, user_telegram_id, order_id
) -> bool:
    """
    Выполняет проверку цифровой подписи.

    Returns:
        True, если проверка пройдена, False - если нет.
    """
    signature = calculate_signature(
        settings.MRH_LOGIN,
        out_sum,
        inv_id,
        password,
        user_id,
        user_telegram_id,
        order_id,
        is_result=True,
    )
    return signature.lower() == received_signature.lower()
