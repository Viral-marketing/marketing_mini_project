import os

from .base import *
from celery.schedules import crontab

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("DB_HOST", "db"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

CELERY_BEAT_SCHEDULE = {
    'daily-analysis-task': {
        'task':'apps.analysis.tasks.daily_analysis',
        # minute을 */1로 하면 1분마다 메일 발송함
        'schedule': crontab(hour=0, minute=0),# 자정이 되면 daily_analysis 함수 호출
    },
}