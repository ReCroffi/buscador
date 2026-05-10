from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PriceHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    store_slug: str
    price: Decimal
    pix_price: Decimal | None
    shipping_price: Decimal | None
    total_price: Decimal
    collected_at: datetime


class HistoryStats(BaseModel):
    lowest_price: Decimal | None
    average_price: Decimal | None
    samples: int
    trend: str
    points: list[PriceHistoryRead]

