from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from apps.analysis.models import Analysis
from apps.analysis.serializers import AnalysisPostSerializer, AnalysisSerializer
from apps.analysis.tasks import process_analysis
from apps.transactions.services import CustomPermissionService


@extend_schema(summary="거래내역 분석 조회 및 생성")
class AnalysisViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = AnalysisSerializer
    permission_classes = [CustomPermissionService]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AnalysisPostSerializer
        return AnalysisSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Analysis.objects.all()
        return Analysis.objects.filter(user=self.request.user)

    @extend_schema(
        summary="특정기간 소비 또는 수입 분석 요청",
        description="""
        본인의 이메일로 분석결과를 발송합니다, 소비는 WITHDRAW, 
        수입은 DEPOSIT을 입력해주세요
        """,
    )
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = {
            "type": "CUSTOM",
            "about": serializer.validated_data["about"],
            "period_start": serializer.validated_data["period_start"],
            "period_end": serializer.validated_data["period_end"],
        }
        user = {
            "id": request.user.id,
            "name": request.user.name,
            "email": request.user.email,
        }
        process_analysis.delay(user, data)
        return Response(
            {"message": "분석이 완료되면 이메일로 발송해드립니다"},
            status=status.HTTP_201_CREATED,
        )
