from django.test import TestCase
from rest_framework import serializers

from apps.transactions.serializers import TransactionSerializer
from apps.transactions.tests.base import (
    CreateTestAccount,
    CreateTestTransaction,
    CreateTestUser,
)


class TransactionSerializerTest(TestCase):
    def test_transactionserializer(self):
        self.user = CreateTestUser.create_test_user()
        self.account = CreateTestAccount.create_test_account(self.user)
        transaction_data = CreateTestTransaction.create_test_transaction_data(
            account=self.account, type="DEPOSIT", amount=-100.97
        )
        self.serializer = TransactionSerializer(data=transaction_data)

        with self.assertRaises(serializers.ValidationError) as cm:
            self.serializer.is_valid(raise_exception=True)

        self.assertIn("거래금액은 0보다 커야합니다", str(cm.exception))
