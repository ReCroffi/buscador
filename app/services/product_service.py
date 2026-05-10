from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.services.normalization import normalize_text


async def get_or_create_product(session: AsyncSession, query: str, sku: str | None = None) -> Product:
    normalized = normalize_text(query)
    product = await session.scalar(select(Product).where(Product.normalized_query == normalized))
    if product:
        return product
    product = Product(query=query, normalized_query=normalized, sku=sku)
    session.add(product)
    await session.flush()
    return product

