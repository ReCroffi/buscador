from celery import Celery

from app.core.config import settings

celery_app = Celery("buscador", broker=str(settings.redis_url), backend=str(settings.redis_url))
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="America/Sao_Paulo",
    beat_schedule={
        "monitor-alerts-every-5-minutes": {
            "task": "app.tasks.monitoring.evaluate_alerts",
            "schedule": 300.0,
        }
    },
)

