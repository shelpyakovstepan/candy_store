# THIRDPARTY
from faststream import FastStream

# FIRSTPARTY
from app.rabbitmq.broker import broker, rabbitmq_connection
from app.rabbitmq.utils import add_phone_number

if rabbitmq_connection():
    faststream_app = FastStream(broker)
else:
    raise ConnectionError("RabbitMQ connection failed")


@broker.subscriber("phone-number-queue")
async def handler_add_phone_number(message):
    """Слушает RabbitMQ очередь: phone-number-queue и выполняет функцию add_phone_number() при получении сообщения."""
    await add_phone_number(message=message)
