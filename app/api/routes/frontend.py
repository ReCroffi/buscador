from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.offer import SearchRequest
from app.services.search_service import SearchService

router = APIRouter(tags=["frontend"])


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return request.app.state.templates.TemplateResponse("dashboard.html", {"request": request, "offers": [], "query": ""})


@router.post("/ui/search", response_class=HTMLResponse)
async def ui_search(
    request: Request,
    query: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    payload = SearchRequest(query=query)
    response = await SearchService(session, redis=getattr(request.app.state, "redis", None)).search(
        payload.query, limit_per_store=payload.limit_per_store, strict=True
    )
    return request.app.state.templates.TemplateResponse(
        "partials/offers.html",
        {"request": request, "offers": response.offers, "query": query},
    )

