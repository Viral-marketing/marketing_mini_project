from django.db import models
from apps.common.constants import ACCOUNT_TYPE, BANK_CODES


class Account(models.Model):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="accounts"
    )
    account_number = models.CharField(max_length=20, unique=True)
    bank_code = models.CharField(max_length=10, choices=BANK_CODES)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = "accounts"

    def __str__(self):
        return f"{self.bank_code} - {self.account_number}"
