from collections.abc import Sequence
from decimal import Decimal
from typing import TypeVar

from app.schemas.offer import OfferRead, ScrapedOffer

OfferT = TypeVar("OfferT", ScrapedOffer, OfferRead)


def money_or_large(value: Decimal | None) -> Decimal:
    return value if value is not None else Decimal("999999999")


def sort_offers(offers: Sequence[OfferT]) -> list[OfferT]:
    return sorted(
        offers,
        key=lambda offer: (
            money_or_large(offer.total_price),
            money_or_large(offer.pix_price),
            -(offer.discount_percent or Decimal("0")),
            money_or_large(offer.shipping_price),
        ),
    )


def detect_false_discount(current_price: Decimal | None, historical_average: Decimal | None, discount_percent: Decimal | None) -> bool:
    if not current_price or not historical_average or not discount_percent:
        return False
    return discount_percent >= Decimal("10") and current_price >= historical_average


def trend_from_prices(prices: list[Decimal]) -> str:
    if len(prices) < 3:
        return "insufficient_data"
    recent = sum(prices[-3:]) / Decimal("3")
    previous = sum(prices[:3]) / Decimal("3")
    if recent < previous * Decimal("0.97"):
        return "falling"
    if recent > previous * Decimal("1.03"):
        return "rising"
    return "stable"
