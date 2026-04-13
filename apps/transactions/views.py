from decimal import Decimal, InvalidOperation

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics
from rest_framework.exceptions import ValidationError

from apps.transactions.serializers import (
    TransactionSerializer,
    TransactionUpdateSerializer,
)
from apps.transactions.services import (
    CustomPermissionService,
    TransactionDetailService,
    TransactionListService,
)


class TransactionListView(generics.ListCreateAPIView):
    # queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = (CustomPermissionService,)  # 로그인 유저 검증 및 권한체크

    @extend_schema(
        summary="거래 내역 목록 조회 및 검색",
        description="사용자의 거래 내역을 조회 계좌, 타입, 금액으로 필터링이 가능",
        parameters=[
            OpenApiParameter(
                "account",
                OpenApiTypes.INT,
                description="계좌 ID 필터,삭제된 계좌의 거래내역 조회 시 0 입력"),
            OpenApiParameter(
                "transaction_type",
                OpenApiTypes.STR,
                description="DEPOSIT(입금) 또는 WITHDRAW(출금)",
            ),
            OpenApiParameter(
                "transaction_amount",
                OpenApiTypes.DECIMAL,
                description="입력한 금액 이상의 거래내역 조회",
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="새로운 거래 내역 생성",
        description="입금 또는 출금 거래를 생성하고 계좌 잔액을 최신화합니다.",
        request=TransactionSerializer,
        responses={201: TransactionSerializer},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

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
            transaction_amount = self.request.GET.get("transaction_amount")
            # request에서 transaction_amount를 transaction_amount에 할당
            if transaction_amount:  # transaction_amount가 있으면
                try:
                    transaction_amount = Decimal(transaction_amount)
                except (InvalidOperation, ValueError, Exception) as e:
                    raise ValidationError(
                        {"transaction_amount": "유효한 숫자를 입력해주세요"}
                    ) from e

        # 모든 조건들이 입력되지 않으면 ListCreateAPIView는 pk를 입력받지 않는 url이므로
        # 한 user의 여러 account에 대한 transaction으로 필터링됨
        return TransactionListService.transaction_list(
            self.request.user, account, transaction_type, transaction_amount
        )

    def perform_create(self, serializer):
        user = self.request.user
        transaction_data = serializer.validated_data
        result = TransactionListService.transaction_create(user, transaction_data)
        serializer.instance = result
        """
        내장 create 메서드가 실행되는 중에 perform_create이 실행됨 
        그래서 serializer의 객체에 결과 result 할당하고 따로 리턴은 없어도 됨
        """


class TransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    # queryset = Transaction.objects.all()
    permission_classes = (CustomPermissionService,)
    lookup_field = "id"
    lookup_url_kwarg = "transaction_pk"

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return TransactionUpdateSerializer
        return TransactionSerializer

    @extend_schema(
        summary="특정계좌의 특정 거래내역 단일 조회",
        description="사용자의 거래 내역을 단일 조회",
        parameters=[
            OpenApiParameter("account", OpenApiTypes.INT, description="계좌 ID 필터"),
            OpenApiParameter(
                "transaction_type",
                OpenApiTypes.STR,
                description="DEPOSIT(입금) 또는 WITHDRAW(출금)",
            ),
            OpenApiParameter(
                "transaction_amount",
                OpenApiTypes.DECIMAL,
                description="입력한 금액 이상의 거래내역 조회",
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="특정계좌의 특정 거래내역 전체 수정",
        description="사용자의 특정 거래 내역 정보를 전체 수정",
        request=TransactionUpdateSerializer,
        responses={201: TransactionUpdateSerializer},
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @extend_schema(
        summary="특정계좌의 특정 거래내역 일부 수정",
        description="사용자의 특정 거래 내역의 일부 수정",
        request=TransactionUpdateSerializer,
        responses={201: TransactionUpdateSerializer},
    )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="특정계좌의 특정 거래내역 삭제",
        description="사용자의 특정 거래 내역을 삭제",
        request=TransactionSerializer,
        responses={201: TransactionSerializer},
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def get_queryset(self):
        """
        RetrieveUpdateDestroyAPIView는 url에 pk를 경로매개변수를 받으므로
        사용자의 계좌 목록 중 특정 계좌에 대한 거래내역이 필터링됨
        """
        return TransactionDetailService.transaction_detail(self.request.user)

    # 나머지 수정 삭제 단일조회는 기본적인 내장 기능을 사용
