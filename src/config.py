import os
from pydantic_settings import BaseSettings, SettingsConfigDict

# За замовчуванням використовуємо sandbox
ENV = os.getenv("ENV", "sandbox")


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    DEBUG: bool = False
    ALGORITHM: str = "HS256"

    model_config = SettingsConfigDict(env_file=f".env.{ENV}")


settings = Settings()
