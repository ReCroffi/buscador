from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.db.session import AsyncSessionLocal
from app.services.alert_service import AlertService


def build_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="America/Sao_Paulo")

    async def evaluate() -> None:
        async with AsyncSessionLocal() as session:
            await AlertService(session).evaluate_all()

    scheduler.add_job(evaluate, "interval", minutes=5, id="evaluate-alerts", max_instances=1)
    return scheduler

