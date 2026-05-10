from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import PriceAlert
from app.models.offer import Offer
from app.models.product import Product
from app.models.store import Store
from app.notifications.email import EmailNotifier
from app.notifications.telegram import TelegramNotifier
from app.schemas.alert import AlertCreate
from app.services.product_service import get_or_create_product


class AlertService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, payload: AlertCreate) -> PriceAlert:
        product = await get_or_create_product(self.session, payload.query)
        alert = PriceAlert(
            product_id=product.id,
            target_price=payload.target_price,
            store_slug=payload.store_slug,
            email=str(payload.email) if payload.email else None,
            telegram_chat_id=payload.telegram_chat_id,
            frequency_minutes=payload.frequency_minutes,
        )
        self.session.add(alert)
        await self.session.commit()
        await self.session.refresh(alert)
        return alert

    async def evaluate_all(self) -> int:
        stmt = select(PriceAlert).where(PriceAlert.enabled.is_(True))
        alerts = (await self.session.scalars(stmt)).all()
        triggered = 0
        for alert in alerts:
            if await self.evaluate(alert):
                triggered += 1
        await self.session.commit()
        return triggered

    async def evaluate(self, alert: PriceAlert) -> bool:
        product = await self.session.get(Product, alert.product_id)
        if product is None:
            return False
        stmt = select(Offer, Store).join(Store, Store.id == Offer.store_id).where(Offer.product_id == product.id)
        if alert.store_slug:
            stmt = stmt.where(Store.slug == alert.store_slug)
        stmt = stmt.order_by(Offer.total_price.asc().nullslast(), Offer.pix_price.asc().nullslast()).limit(1)
        row = (await self.session.execute(stmt)).first()
        if not row:
            return False
        offer, store = row
        current = offer.total_price or offer.pix_price or offer.current_price
        if not current:
            return False
        alert.last_seen_price = current
        if current > alert.target_price or self._recently_triggered(alert):
            return False
        await self._notify(alert, product.query, store.name, current, offer.url)
        alert.last_triggered_at = datetime.now(UTC)
        return True

    @staticmethod
    def _recently_triggered(alert: PriceAlert) -> bool:
        if not alert.last_triggered_at:
            return False
        cooldown = timedelta(minutes=max(alert.frequency_minutes, 30))
        return datetime.now(UTC) - alert.last_triggered_at < cooldown

    async def _notify(self, alert: PriceAlert, product: str, store: str, current: Decimal, url: str) -> None:
        if alert.telegram_chat_id:
            await TelegramNotifier().send_price_alert(
                chat_id=alert.telegram_chat_id,
                product=product,
                store=store,
                current_price=current,
                target_price=alert.target_price,
                url=url,
            )
        if alert.email:
            await EmailNotifier().send_price_alert(
                to_email=alert.email,
                product=product,
                store=store,
                current_price=current,
                target_price=alert.target_price,
                url=url,
            )

