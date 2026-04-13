from django.contrib.auth import get_user_model

from apps.accounts.models import Account
from apps.transactions.models import Transaction

User = get_user_model()


class CreateTestUser:
    @staticmethod
    def create_test_user():
        return User.objects.create_user(
            name="test_user",
            email="test_for_transaction@test.com",
            password="test_password",
        )

    @staticmethod
    def create_test_other_user():
        return User.objects.create_user(
            name="other_user", email="other@test.com", password="other_password"
        )

    @staticmethod
    def create_test_staff():
        return User.objects.create_user(
            name="test_staff",
            email="staff@staff.com",
            password="test_staff_password",
            is_staff=True,
            is_superuser=False,
        )

    @staticmethod
    def create_test_superuser():
        return User.objects.create_user(
            name="superuser",
            email="super@super.com",
            password="super_password",
            is_superuser=True,
        )


class CreateTestAccount:
    @staticmethod
    def create_test_account(user):
        return Account.objects.create(
            user=user,
            account_number="1234567890",
            bank_code="001",
            account_type="CHECKING",
            balance=100000.07,
        )


class CreateTestTransaction:
    @staticmethod
    def create_test_transaction_data(account, type, amount):
        """
        Creates test transaction data
        account: Account object
        transaction_type: TransactionType object
        transaction_amount: TransactionAmount object
        """
        return {
            "account": account.id,
            "transaction_type": type,
            "transaction_method": "ATM",
            "transaction_amount": amount,
        }

    @staticmethod
    def create_test_transaction(
        account,
        user,
        transaction_type,
        transaction_method,
        transaction_amount,
        balance_after,
        memo,
    ):
        return Transaction.objects.create(
            account=account,
            user=user,
            transaction_type=transaction_type,
            transaction_method=transaction_method,
            transaction_amount=transaction_amount,
            balance_after=balance_after,
            memo=memo,
        )

    @staticmethod
    def create_test_DEPOSIT_transaction(account, user):
        return Transaction.objects.create(
            account=account,
            user=user,
            transaction_type="DEPOSIT",
            transaction_method="ATM",
            transaction_amount=100000.08,
            balance_after=account.balance,
            memo="test_DEPOSIT_memo",
        )
