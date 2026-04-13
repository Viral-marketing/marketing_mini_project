from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.analysis.views import AnalysisViewSet

app_name = "celery"

router = DefaultRouter()
router.register(r"celery", AnalysisViewSet, basename="celery")

urlpatterns = [path("", include(router.urls))]
