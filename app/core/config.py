from functools import lru_cache
from typing import Annotated

from pydantic import AnyHttpUrl, EmailStr, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Buscador de Precos"
    environment: str = "local"
    debug: bool = False
    secret_key: str = "change-me"

    database_url: str = Field(
        default="postgresql+asyncpg://buscador:buscador@postgres:5432/buscador"
    )
    sync_database_url: str = Field(
        default="postgresql+psycopg://buscador:buscador@postgres:5432/buscador"
    )
    redis_url: str = Field(default="redis://redis:6379/0")

    scrape_timeout_seconds: float = 25.0
    scrape_concurrency: int = 6
    exact_match_threshold: int = 88
    strict_match_threshold: int = 94
    request_user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0 Safari/537.36"
    )
    proxy_urls: list[AnyHttpUrl] = []

    telegram_bot_token: str | None = None
    telegram_webhook_secret: str | None = None
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from_email: EmailStr | None = None
    smtp_tls: bool = True

    allowed_origins: list[str] = ["http://localhost:8000", "http://127.0.0.1:8000"]
    rate_limit_per_minute: Annotated[int, Field(gt=0)] = 60

    @field_validator(
        "telegram_bot_token",
        "telegram_webhook_secret",
        "smtp_host",
        "smtp_user",
        "smtp_password",
        "smtp_from_email",
        mode="before",
    )
    @classmethod
    def empty_string_as_none(cls, value: str | None) -> str | None:
        return None if value == "" else value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
