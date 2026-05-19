from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    jwt_secret: str = "dev-secret"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    db_url: str = "postgresql://shop:shop@localhost:5432/shop"
    rabbitmq_url: str = "amqp://shop:shop@localhost:5672/"


settings = Settings()
