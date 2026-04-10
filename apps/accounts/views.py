from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, viewsets

from apps.transactions.services import CustomPermissionService

from .models import Account
from .serializers import AccountSerializer


@extend_schema_view(
    list=extend_schema(
        summary="계좌 목록 조회",
        description="로그인한 사용자의 모든 계좌내역을 조회합니다.",
    ),
    retrieve=extend_schema(
        summary="계좌 상세 조회",
        description="특정 계좌의 상세 내역을 조회합니다.",
    ),
    create=extend_schema(
        summary="계좌 등록",
        description="새로운 계좌를 등록합니다.",
    ),
    destroy=extend_schema(summary="계좌 삭제", description="계좌를 삭제합니다."),
)
class AccountViewSet(
    mixins.CreateModelMixin,  # 계좌 생성
    mixins.ListModelMixin,  # 사용자의 모든 계좌 목록 조회
    mixins.RetrieveModelMixin,  # 특정 계좌 상세 조회
    mixins.DestroyModelMixin,  # 계좌 삭제
    viewsets.GenericViewSet,
):
    serializer_class = AccountSerializer
    # 직접 정의한 로직에 따라 API 접근 권한 검사
    permission_classes = (CustomPermissionService,)

    def get_queryset(self):
        # 사용자가 접근할 수 있는 데이터의 범위 결정
        # 요청을 보낸 사용자의 계좌만 필터링해서 반환
        return Account.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # 사용자가 입력하지 않은 현재 로그인 유저를 서버가 직접 찾아 DB에 자동으로 저장
        # 저장할 때 user 필드에 로그인한 사용자의 정보를 강제로 주입
        serializer.save(user=self.request.user)
