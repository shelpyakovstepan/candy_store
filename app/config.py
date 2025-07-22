# STDLIB
import hashlib
import os
from typing import Literal

# THIRDPARTY
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MODE: Literal["DEV", "PROD", "TEST"]

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    REDIS_HOST: str
    REDIS_PORT: int

    RABBIT_USER: str
    RABBIT_PASS: str
    RABBIT_HOST: str
    RABBIT_PORT: int

    SECRET_KEY: str
    ALGORITHM: str

    BOT_TOKEN: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    )


settings = Settings()  # pyright: ignore [reportCallIssue]


def get_db_url():
    return (
        f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}@"
        f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )


def get_redis_url():
    return f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"


def get_rabbitmq_url():
    return (
        f"amqp://{settings.RABBIT_USER}:{settings.RABBIT_PASS}@"
        f"{settings.RABBIT_HOST}:{settings.RABBIT_PORT}/"
    )


def get_bot_token_hash():
    return hashlib.sha256(settings.BOT_TOKEN.encode())
