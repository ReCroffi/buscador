from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from redis.asyncio import Redis

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.session import AsyncSessionLocal
from app.services.store_service import ensure_stores


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    configure_logging()
    app.state.templates = Jinja2Templates(directory="app/templates")
    app.state.redis = Redis.from_url(str(settings.redis_url), decode_responses=True)
    try:
        await app.state.redis.ping()
    except Exception:
        await app.state.redis.aclose()
        app.state.redis = None
    try:
        async with AsyncSessionLocal() as session:
            await ensure_stores(session)
    except Exception:
        pass
    yield
    if app.state.redis:
        await app.state.redis.aclose()


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(api_router)


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.app_name}
