from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.transactions.tests.base import (
    CreateTestAccount,
    CreateTestTransaction,
    CreateTestUser,
)


class TransactionViewTest(APITestCase):
    def test_get_queryset(self):
        self.user = CreateTestUser.create_test_user()
        self.superuser = CreateTestUser.create_test_superuser()
        self.account = CreateTestAccount.create_test_account(user=self.user)
        self.transaction = CreateTestTransaction.create_test_transaction(
            account=self.account,
            transaction_type="DEPOSIT",
            transaction_method="ATM",
            transaction_amount=1000.96,
            memo="test transaction",
            balance_after=self.account.balance,
        )
        self.transaction.save()
        self.url = reverse("transactions:list")

        self.client.force_login(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["account"], self.account.id)

        self.client.force_login(user=self.superuser)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["account"], self.account.id)

    def test_perform_create(self):
        self.user = CreateTestUser.create_test_user()
        self.account = CreateTestAccount.create_test_account(user=self.user)
        self.transaction = CreateTestTransaction.create_test_transaction_data(
            account=self.account,
            type="DEPOSIT",
            amount=1000.95,
        )
        url = reverse("transactions:list")
        self.client.force_login(user=self.user)
        response = self.client.post(url, data=self.transaction)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal(response.data["balance_after"]))


class TransactionDetailViewTest(APITestCase):
    def test_get_queryset(self):
        self.user = CreateTestUser.create_test_user()
        self.other_user = CreateTestUser.create_test_other_user()
        self.superuser = CreateTestUser.create_test_superuser()
        self.account = CreateTestAccount.create_test_account(user=self.user)
        self.transaction = CreateTestTransaction.create_test_transaction(
            account=self.account,
            transaction_type="DEPOSIT",
            transaction_method="ATM",
            transaction_amount=1000.85,
            memo="test transaction",
            balance_after=self.account.balance,
        )
        self.other_transaction = CreateTestTransaction.create_test_transaction(
            account=self.account,
            transaction_type="WITHDRAW",
            transaction_method="ATM",
            transaction_amount=1000.46,
            memo="test transaction",
            balance_after=self.account.balance,
        )
        self.transaction.save()
        self.url = reverse(
            "transactions:detail", kwargs={"transaction_pk": self.transaction.id}
        )

        self.client.force_login(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.transaction.id)

        self.client.force_login(user=self.superuser)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.transaction.id)

        self.client.force_login(user=self.other_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
