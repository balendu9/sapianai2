from celery import Celery
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "sapienai",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.daily_ai_messages"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        'daily-ai-messages': {
            'task': 'app.tasks.daily_ai_messages.send_daily_ai_messages',
            'schedule': {'hour': 14, 'minute': 0},  # 2 PM UTC daily
        },
    },
)
