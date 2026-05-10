from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class OfferBase(BaseModel):
    title: str
    store: str
    url: str
    image_url: str | None = None
    current_price: Decimal | None = None
    pix_price: Decimal | None = None
    installment_price: Decimal | None = None
    shipping_price: Decimal | None = None
    total_price: Decimal | None = None
    availability: str = "unknown"
    coupon_code: str | None = None
    discount_percent: Decimal | None = None
    match_score: int = 0
    collected_at: datetime | None = None


class OfferRead(OfferBase):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None


class ScrapedOffer(OfferBase):
    external_id: str
    store_slug: str


class SearchRequest(BaseModel):
    query: str = Field(min_length=3, max_length=255)
    stores: list[str] | None = None
    limit_per_store: int = Field(default=12, ge=1, le=50)
    strict: bool = True


class SearchResponse(BaseModel):
    query: str
    normalized_query: str
    total: int
    offers: list[OfferRead]


class Coupon(BaseModel):
    code: str
    description: str | None = None
    url: HttpUrl | None = None

