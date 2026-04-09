from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.models import Account
from apps.transactions.models import Transaction
from apps.transactions.serializers import TransactionSerializer
from apps.transactions.services import TransactionListService

User = get_user_model()


class TransactionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="test_user",
            username="test_user",
            email="test@test.com",
            password="test",
        )
        self.account = Account.objects.create(
            user=self.user,
            account_number="1234567890",
            bank_code="001",
            account_type="CHECKING",
            balance=100,
        )

    # model test
    def test_create_transaction(self):
        transaction = Transaction.objects.create(
            account=self.account,
            transaction_amount=10.02,
            transaction_type="DEPOSIT",
            transaction_method="ATM",
            memo="test_meno",
            balance_after=self.account.balance + Decimal("10.02"),
        )
        self.assertEqual(Transaction.objects.count(), 1)
        self.assertEqual(self.account, transaction.account)
        self.assertEqual(transaction.account.user, self.user)
        self.account.refresh_from_db()
        self.assertEqual(transaction.balance_after, Decimal("110.02"))


class TransactionSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="test_user",
            username="test_user",
            email="test@test.com",
            password="test",
        )
        self.account = Account.objects.create(
            user=self.user,
            account_number="1234567890",
            bank_code="001",
            account_type="CHECKING",
            balance=100,
        )
        self.transaction = Transaction.objects.create(
            account=self.account,
            transaction_amount=10.02,
            transaction_type="DEPOSIT",
            transaction_method="ATM",
            memo="test_meno",
            balance_after=self.account.balance + Decimal("10.02"),
        )
        # serializer test

    def test_transaction_serializers(self):
        serializer = TransactionSerializer(instance=self.transaction)
        self.assertEqual(serializer.data["account"], self.account.pk)
        self.assertEqual(serializer.data["transaction_amount"], "10.02")
        self.assertEqual(serializer.data["transaction_type"], "DEPOSIT")
        self.assertEqual(serializer.data["transaction_method"], "ATM")
        self.assertEqual(serializer.data["memo"], "test_meno")


class TransactionServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="test_user",
            username="test_user",
            email="test@test.com",
            password="test",
        )
        self.account = Account.objects.create(
            user=self.user,
            account_number="1234567890",
            bank_code="001",
            account_type="CHECKING",
            balance=100,
        )

    # service test
    def test_transaction_service(self):
        transaction = TransactionListService.transaction_create(
            user=self.user,
            account=self.account,
            transaction_type="DEPOSIT",
            transaction_method="ATM",
            transaction_amount=10.02,
            memo="test_meno",
        )
        self.assertEqual(self.account, transaction.account)
        self.assertEqual(transaction.account.user, self.user)
        self.account.refresh_from_db()
        self.assertEqual(transaction.balance_after, self.account.balance)
