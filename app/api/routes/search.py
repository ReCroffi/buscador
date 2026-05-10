from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import rate_limit
from app.db.session import get_session
from app.schemas.offer import SearchRequest, SearchResponse
from app.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["search"], dependencies=[Depends(rate_limit)])


@router.post("", response_model=SearchResponse)
async def search_products(payload: SearchRequest, request: Request, session: AsyncSession = Depends(get_session)):
    redis = getattr(request.app.state, "redis", None)
    return await SearchService(session, redis=redis).search(
        payload.query,
        stores=payload.stores,
        limit_per_store=payload.limit_per_store,
        strict=payload.strict,
    )

