from .models import Account
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from .serializers import AccountSerializer


class AccountViewSet(
    mixins.CreateModelMixin,  # 계좌 생성
    mixins.ListModelMixin,  # 사용자의 모든 계좌 목록 조회
    mixins.RetrieveModelMixin,  # 특정 계좌 상세 조회
    mixins.DestroyModelMixin,  # 계좌 삭제
    viewsets.GenericViewSet,
):
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 사용자가 접근할 수 있는 데이터의 범위 결정
        # 요청을 보낸 사용자의 계좌만 필터링해서 반환
        return Account.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # 사용자가 입력하지 않은 현재 로그인 유저를 서버가 직접 찾아 DB에 자동으로 저장
        # 저장할 때 user 필드에 로그인한 사용자의 정보를 강제로 주입
        serializer.save(user=self.request.user)
