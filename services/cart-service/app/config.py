from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    jwt_secret: str = "dev-secret"
    jwt_algorithm: str = "HS256"
    db_url: str = "postgresql://shop:shop@localhost:5432/shop"
    redis_url: str = "redis://localhost:6379/1"


settings = Settings()
