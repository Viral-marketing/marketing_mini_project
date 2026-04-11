from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.analysis.views import AnalysisViewSet

app_name = 'analysis'

router = DefaultRouter()
router.register(r"analysis",AnalysisViewSet, basename="analysis")

urlpatterns = [
    path('',include(router.urls))
]
