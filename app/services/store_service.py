from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.store import Store
from app.scrapers.registry import STORE_SEED


async def ensure_stores(session: AsyncSession) -> None:
    existing = {row[0] for row in (await session.execute(select(Store.slug))).all()}
    for store in STORE_SEED:
        if store["slug"] not in existing:
            session.add(Store(**store, enabled=True))
    await session.commit()


async def get_store_by_slug(session: AsyncSession, slug: str) -> Store:
    store = await session.scalar(select(Store).where(Store.slug == slug))
    if store is None:
        seed = next((item for item in STORE_SEED if item["slug"] == slug), None)
        if not seed:
            raise ValueError(f"unknown store: {slug}")
        store = Store(**seed, enabled=True)
        session.add(store)
        await session.flush()
    return store

