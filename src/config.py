import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Визначення поточного середовища (за замовчуванням sandbox)
ENV: str = os.getenv("ENV", "sandbox").lower()

BASE_DIR = Path(__file__).resolve().parent.parent
env_file_path = BASE_DIR / f".env.{ENV}"


class Settings(BaseSettings):
    ENV: str = ENV
    DATABASE_URL: str = f"sqlite:///./{ENV}.db"
    SECRET_KEY: str = "super-secret-zombie-key-default"
    DEBUG: bool = True if ENV == "sandbox" else False
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ADMIN_SECRET_KEY: str = "zombie-overlord-sandbox-master-token"

    model_config = SettingsConfigDict(
        env_file=str(env_file_path) if env_file_path.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
