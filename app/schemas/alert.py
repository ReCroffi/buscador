from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class AlertCreate(BaseModel):
    query: str = Field(min_length=3, max_length=255)
    target_price: Decimal = Field(gt=0)
    store_slug: str | None = None
    email: EmailStr | None = None
    telegram_chat_id: str | None = None
    frequency_minutes: int = Field(default=60, ge=5, le=1440)

    @model_validator(mode="after")
    def has_channel(self) -> "AlertCreate":
        if not self.email and not self.telegram_chat_id:
            raise ValueError("configure email or telegram_chat_id")
        return self


class AlertRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    target_price: Decimal
    store_slug: str | None
    email: str | None
    telegram_chat_id: str | None
    frequency_minutes: int
    enabled: bool
    last_triggered_at: datetime | None
    last_seen_price: Decimal | None
    created_at: datetime


class AlertUpdate(BaseModel):
    target_price: Decimal | None = Field(default=None, gt=0)
    store_slug: str | None = None
    email: EmailStr | None = None
    telegram_chat_id: str | None = None
    frequency_minutes: int | None = Field(default=None, ge=5, le=1440)
    enabled: bool | None = None

