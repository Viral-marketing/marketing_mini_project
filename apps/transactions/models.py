from django.contrib.auth import get_user_model
from django.db import models

from apps.accounts.models import Account
from apps.common.constants import TRANSACTION_METHOD, TRANSACTION_TYPE

User = get_user_model()


class Transaction(models.Model):
    # # 거래 타입
    # TRANSACTION_TYPE = [
    #     ("DEPOSIT", "입금"),
    #     ("WITHDRAW", "출금"),
    # ]
    #
    # # 거래 종류
    # TRANSACTION_METHOD = [
    #     ("ATM", "ATM 거래"),
    #     ("TRANSFER", "계좌이체"),
    #     ("AUTOMATIC_TRANSFER", "자동이체"),
    #     ("CARD", "카드결제"),
    #     ("INTEREST", "이자"),
    # ]

    account = models.ForeignKey(
        Account, on_delete=models.SET_NULL, related_name="transactions", null=True
    )
    # 계좌가 삭제되어도 거래기록은 남아있어야함
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="transactions"
    )
    transaction_amount = models.DecimalField(max_digits=20, decimal_places=2)
    # 소수점 2자리까지 표시, 18자리 까지 표시가능
    transaction_type = models.CharField(
        choices=TRANSACTION_TYPE, max_length=20, default="DEPOSIT"
    )
    # type으로 입금인지 출금인지 확인 출금이면 비지니스로직에서 '-' 추가 필요
    transaction_method = models.CharField(
        choices=TRANSACTION_METHOD, max_length=20, default="ATM"
    )
    balance_after = models.DecimalField(max_digits=20, decimal_places=2, editable=False)
    memo = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transaction"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["account"]),
            models.Index(
                fields=["transaction_type", "transaction_amount", "transaction_method"]
            ),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.account}거래내역"
