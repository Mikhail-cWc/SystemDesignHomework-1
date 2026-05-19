from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    rabbitmq_url: str = "amqp://shop:shop@localhost:5672/"


settings = Settings()
