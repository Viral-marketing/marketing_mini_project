from drf_spectacular.utils import extend_schema
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response

from apps.analysis.models import Analysis
from apps.analysis.serializers import AnalysisSerializer,AnalysisPostSerializer
from apps.analysis.tasks import process_spending_analysis
from apps.transactions.services import CustomPermissionService

@extend_schema(
    summary="거래내역 분석 조회 및 생성"
)
class AnalysisViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = AnalysisSerializer
    permission_classes = [CustomPermissionService]

    def get_serializer_class(self):
        if self.request.method =="POST":
            return AnalysisPostSerializer
        return AnalysisSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Analysis.objects.all()
        return Analysis.objects.filter(user=self.request.user)

    @extend_schema(
        summary="분석 이메일 발송 요청",
        description="본인의 이메일로 분석결과를 발송합니다"
    )
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        data = serializer.is_valid(raise_exception=True)
        process_spending_analysis.delay(request.user.email,request.user.id,data)
        return Response(
            {"message":"분석이 완료되면 이메일로 발송해드립니다"},
            status=status.HTTP_201_CREATED
        )