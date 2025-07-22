# THIRDPARTY
from faststream.rabbit import RabbitBroker
from kombu import Connection

# FIRSTPARTY
from app.config import get_rabbitmq_url
from app.logger import logger

conn_url = get_rabbitmq_url()


def rabbitmq_connection():
    try:
        with Connection(conn_url) as conn:
            conn.connect()
            logger.info("Successfully connected to RabbitMQ")
            return True
    except Exception as e:
        logger.error(f"RabbitMQ connection failed: {str(e)}", exc_info=True)
        return False


if rabbitmq_connection():
    broker = RabbitBroker(conn_url)
    logger.info("Successfully connected to FastStream RabbitMQ")
else:
    raise ConnectionError("RabbitMQ connection failed")


async def send_message(message, queue):
    await broker.publish(message, queue)
