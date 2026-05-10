from fastapi import APIRouter

from app.api.routes import alerts, frontend, history, search, telegram

api_router = APIRouter()
api_router.include_router(frontend.router)
api_router.include_router(search.router, prefix="/api")
api_router.include_router(alerts.router, prefix="/api")
api_router.include_router(history.router, prefix="/api")
api_router.include_router(telegram.router, prefix="/api")

