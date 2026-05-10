import structlog
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.offer import Offer
from app.models.price_history import PriceHistory
from app.models.store import Store
from app.schemas.offer import OfferRead, ScrapedOffer, SearchResponse
from app.scrapers.base import run_scrapers
from app.scrapers.registry import get_scrapers
from app.services.matching import ExactProductMatcher
from app.services.normalization import normalize_text
from app.services.pricing import sort_offers
from app.services.product_service import get_or_create_product
from app.services.store_service import get_store_by_slug

logger = structlog.get_logger(__name__)


class SearchService:
    def __init__(self, session: AsyncSession, redis: Redis | None = None) -> None:
        self.session = session
        self.redis = redis
        self.matcher = ExactProductMatcher()

    async def search(
        self,
        query: str,
        stores: list[str] | None = None,
        limit_per_store: int = 12,
        strict: bool = True,
        persist: bool = True,
    ) -> SearchResponse:
        cache_key = f"search:{normalize_text(query)}:{','.join(stores or [])}:{limit_per_store}:{strict}"
        if self.redis:
            cached = await self.redis.get(cache_key)
            if cached:
                return SearchResponse.model_validate_json(cached)

        scrapers = get_scrapers(stores)
        raw_offers = await run_scrapers(scrapers, query, limit_per_store)
        filtered = self.filter_exact(query, raw_offers, strict=strict)
        ordered = sort_offers(filtered)

        if persist:
            await self.persist(query, ordered)

        response = SearchResponse(
            query=query,
            normalized_query=normalize_text(query),
            total=len(ordered),
            offers=[OfferRead(**offer.model_dump()) for offer in ordered],
        )
        if self.redis:
            await self.redis.setex(cache_key, 300, response.model_dump_json())
        return response

    def filter_exact(self, query: str, offers: list[ScrapedOffer], strict: bool) -> list[ScrapedOffer]:
        accepted: list[ScrapedOffer] = []
        for offer in offers:
            match = self.matcher.match(query, offer.title)
            if match.accepted or not strict:
                accepted.append(offer.model_copy(update={"match_score": match.score}))
            else:
                logger.info(
                    "offer.rejected",
                    store=offer.store_slug,
                    title=offer.title,
                    reason=match.reason,
                    score=match.score,
                )
        return accepted

    async def persist(self, query: str, offers: list[ScrapedOffer]) -> None:
        product = await get_or_create_product(self.session, query)
        for item in offers:
            store = await get_store_by_slug(self.session, item.store_slug)
            total = item.total_price or item.current_price or item.pix_price
            values = {
                "product_id": product.id,
                "store_id": store.id,
                "external_id": item.external_id,
                "title": item.title,
                "normalized_title": normalize_text(item.title),
                "current_price": item.current_price,
                "pix_price": item.pix_price,
                "installment_price": item.installment_price,
                "shipping_price": item.shipping_price,
                "total_price": total,
                "availability": item.availability,
                "url": item.url,
                "image_url": item.image_url,
                "coupon_code": item.coupon_code,
                "discount_percent": item.discount_percent,
                "match_score": item.match_score,
            }
            insert_stmt = insert(Offer).values(**values)
            upsert_stmt = insert_stmt.on_conflict_do_update(
                constraint="uq_offer_store_external",
                set_={key: value for key, value in values.items() if key not in {"store_id", "external_id"}},
            ).returning(Offer.id)
            offer_id = (await self.session.execute(upsert_stmt)).scalar_one()
            if total:
                self.session.add(
                    PriceHistory(
                        product_id=product.id,
                        offer_id=offer_id,
                        store_slug=item.store_slug,
                        price=item.current_price or total,
                        pix_price=item.pix_price,
                        shipping_price=item.shipping_price,
                        total_price=total,
                    )
                )
        await self.session.commit()


async def latest_offers(session: AsyncSession, query: str, limit: int = 50) -> list[OfferRead]:
    normalized = normalize_text(query)
    stmt = (
        select(Offer, Store)
        .join(Store, Store.id == Offer.store_id)
        .where(Offer.normalized_title.contains(normalized.split()[0] if normalized else ""))
        .order_by(Offer.total_price.asc().nullslast(), Offer.pix_price.asc().nullslast())
        .limit(limit)
    )
    rows = (await session.execute(stmt)).all()
    offers = []
    for offer, store in rows:
        offers.append(
            OfferRead(
                id=offer.id,
                title=offer.title,
                store=store.name,
                url=offer.url,
                image_url=offer.image_url,
                current_price=offer.current_price,
                pix_price=offer.pix_price,
                installment_price=offer.installment_price,
                shipping_price=offer.shipping_price,
                total_price=offer.total_price,
                availability=offer.availability,
                coupon_code=offer.coupon_code,
                discount_percent=offer.discount_percent,
                match_score=offer.match_score,
                collected_at=offer.collected_at,
            )
        )
    return offers
