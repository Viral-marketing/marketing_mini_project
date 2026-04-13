import os

from celery.schedules import crontab

from .base import *

DEBUG = True

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
        "NAME": os.getenv("DB_NAME", "django"),
        "USER": os.getenv("DB_USER", "postgres"),
        "PASSWORD": os.getenv("DB_PASSWORD", "postgres"),
    }
}
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

CELERY_BEAT_SCHEDULE = {
    "daily-analysis-task": {
        "task": "apps.analysis.tasks.daily_analysis",
        # minute을 */1로 하면 1분마다 메일 발송함
        "schedule": crontab(hour=0, minute=0),  # 자정이 되면 daily_analysis 함수 호출
    },
}
