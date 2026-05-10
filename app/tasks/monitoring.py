import asyncio

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.alert import PriceAlert
from app.models.product import Product
from app.services.alert_service import AlertService
from app.services.search_service import SearchService
from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.monitoring.evaluate_alerts")
def evaluate_alerts() -> int:
    return asyncio.run(_evaluate_alerts())


@celery_app.task(name="app.tasks.monitoring.refresh_product")
def refresh_product(query: str, stores: list[str] | None = None) -> int:
    return asyncio.run(_refresh_product(query, stores))


async def _evaluate_alerts() -> int:
    async with AsyncSessionLocal() as session:
        alerts = (await session.scalars(select(PriceAlert).where(PriceAlert.enabled.is_(True)))).all()
        queries: set[str] = set()
        for alert in alerts:
            product = await session.get(Product, alert.product_id)
            if product:
                queries.add(product.query)
        search = SearchService(session)
        for query in queries:
            await search.search(query, persist=True)
        return await AlertService(session).evaluate_all()


async def _refresh_product(query: str, stores: list[str] | None = None) -> int:
    async with AsyncSessionLocal() as session:
        response = await SearchService(session).search(query, stores=stores, persist=True)
        return response.total
