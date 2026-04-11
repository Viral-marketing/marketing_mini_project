from rest_framework import mixins,viewsets

from apps.analysis.serializers import AnalysisSerializer
from apps.transactions.services import CustomPermissionService

class AnalysisViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = AnalysisSerializer
    permission_classes = [CustomPermissionService]
