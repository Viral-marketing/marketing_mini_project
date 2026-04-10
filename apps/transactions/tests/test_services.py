from django.test import TestCase
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.transactions.services import CustomPermissionService, TransactionListService
from apps.transactions.tests.base import (
    CreateTestAccount,
    CreateTestTransaction,
    CreateTestUser,
)


class TransactionServiceTests(TestCase):
    def test_transaction_create(self):
        self.user = CreateTestUser.create_test_user()
        self.other_user = CreateTestUser.create_test_other_user()
        self.account = CreateTestAccount.create_test_account(user=self.user)
        transaction_data_for_permission = (
            CreateTestTransaction.create_test_transaction_data(
                account=self.account, type="DEPOSIT", amount=1000.86
            )
        )
        transaction_data_for_validation = (
            CreateTestTransaction.create_test_transaction_data(
                account=self.account,
                type="WITHDRAW",
                amount=10000000.06,
            )
        )
        transaction_data_for_balance = (
            CreateTestTransaction.create_test_transaction_data(
                account=self.account,
                type="DEPOSIT",
                amount=1000.97,
            )
        )

        with self.assertRaises(PermissionDenied) as cm_1:
            self.transaction = TransactionListService.transaction_create(
                user=self.other_user,
                transaction_data=transaction_data_for_permission,
            )
        self.assertIn("본인 계좌에 대한 거래만 가능합니다", str(cm_1.exception))

        with self.assertRaises(ValidationError) as cm_2:
            self.transaction = TransactionListService.transaction_create(
                user=self.user,
                transaction_data=transaction_data_for_validation,
            )
        self.assertIn("잔액이 부족합니다", str(cm_2.exception))

        self.transaction = TransactionListService.transaction_create(
            user=self.user,
            transaction_data=transaction_data_for_balance,
        )
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, self.transaction.balance_after)

    def test_has_permission(self):
        self.user = CreateTestUser.create_test_user()
        self.staff_user = CreateTestUser.create_test_staff()
        self.superuser_user = CreateTestUser.create_test_superuser()

        from rest_framework.test import APIRequestFactory

        self.factory = APIRequestFactory()

        request = self.factory.get("/transactions/")
        request.user = self.user
        permission = CustomPermissionService()
        result = permission.has_permission(request, None)
        self.assertTrue(result)

        request = self.factory.get("/transactions/")
        request.user = self.staff_user
        permission = CustomPermissionService()
        result = permission.has_permission(request, None)
        self.assertTrue(result)

        request = self.factory.post("/transactions/")
        request.user = self.staff_user
        permission = CustomPermissionService()
        result = permission.has_permission(request, None)
        self.assertFalse(result)

        request = self.factory.post("/transactions/")
        request.user = self.superuser_user
        permission = CustomPermissionService()
        result = permission.has_permission(request, None)
        self.assertTrue(result)
