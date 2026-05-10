from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.price_history import PriceHistory
from app.models.product import Product
from app.schemas.history import HistoryStats, PriceHistoryRead
from app.services.normalization import normalize_text
from app.services.pricing import trend_from_prices

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/{query}", response_model=HistoryStats)
async def product_history(query: str, session: AsyncSession = Depends(get_session)):
    product = await session.scalar(select(Product).where(Product.normalized_query == normalize_text(query)))
    if not product:
        raise HTTPException(status_code=404, detail="product not found")
    points = (
        await session.scalars(
            select(PriceHistory)
            .where(PriceHistory.product_id == product.id)
            .order_by(PriceHistory.collected_at.asc())
            .limit(500)
        )
    ).all()
    stats = (
        await session.execute(
            select(func.min(PriceHistory.total_price), func.avg(PriceHistory.total_price), func.count(PriceHistory.id)).where(
                PriceHistory.product_id == product.id
            )
        )
    ).one()
    prices = [Decimal(point.total_price) for point in points]
    return HistoryStats(
        lowest_price=stats[0],
        average_price=stats[1],
        samples=stats[2],
        trend=trend_from_prices(prices),
        points=[PriceHistoryRead.model_validate(point) for point in points],
    )
