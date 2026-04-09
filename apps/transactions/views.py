from decimal import Decimal

from rest_framework import generics

from apps.transactions.models import Transaction
from apps.transactions.serializers import TransactionSerializer
from apps.transactions.services import (
    CustomPermissionService,
    TransactionDetailService,
    TransactionListService,
)


class TransactionListView(generics.ListCreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = (CustomPermissionService,) # 로그인 유저 검증 및 권한체크

    def get_queryset(self):

        # 필터링 조건
        account = None
        transaction_type = None
        transaction_amount = None

        if self.request.GET.get("account"):
           account = self.request.GET.get("account")
        if self.request.GET.get("transaction_type"):
            transaction_type = self.request.GET.get("transaction_type")
        if self.request.GET.get("transaction_amount"):
            transaction_amount = Decimal(self.request.GET.get("transaction_amount"))
        # 모든 조건들이 입력되지 않으면 ListCreateAPIView는 pk를 입력받지 않는 url이므로
        # 한 user의 여러 account에 대한 transaction으로 필터링됨
        return TransactionListService.transaction_list(
            self.request.user,account,transaction_type,transaction_amount
        )

    def perform_create(self,serializer):
        user = self.request.user
        account = serializer.validated_data["account"]
        transaction_type = serializer.validated_data["transaction_type"]
        transaction_method = serializer.validated_data["transaction_method"]
        transaction_amount = serializer.validated_data["transaction_amount"]
        memo = serializer.validated_data["memo"]
        # services에서 정의한 transaction_create을 활용하기 전 변수 설정
        result = TransactionListService.transaction_create(
            user,account,transaction_type,transaction_method,transaction_amount,memo
        )
        serializer.instance = result
        """
        내장 create 메서드가 실행되는 중에 perform_create이 실행됨 
        그래서 serializer의 객체에 결과 result 할당하고 따로 리턴은 없어도 됨
        """


class TransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = (CustomPermissionService,)
    lookup_field = "transaction_pk"

    def get_queryset(self):
        """
        RetrieveUpdateDestroyAPIView는 url에 pk를 경로매개변수를 받으므로
        사용자의 계좌 목록 중 특정 계좌에 대한 거래내역이 필터링됨
        """
        return TransactionDetailService.transaction_detail(
            self.request.user,pk=self.kwargs["transaction_pk"]
        )

    # 나머지 수정 삭제 단일조회는 기본적인 내장 기능을 사용