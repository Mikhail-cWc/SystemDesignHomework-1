from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    jwt_secret: str = "dev-secret"
    jwt_algorithm: str = "HS256"
    db_url: str = "postgresql://shop:shop@localhost:5432/shop"
    mongo_url: str = "mongodb://localhost:27017"
    mongo_db_name: str = "ozon_shop"
    redis_url: str = "redis://localhost:6379/0"
    rabbitmq_url: str = "amqp://shop:shop@localhost:5672/"


settings = Settings()
