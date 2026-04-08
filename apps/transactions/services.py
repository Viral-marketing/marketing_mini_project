from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError
from apps.transactions.models import Transaction

class TransactionListService:
    @staticmethod
    def transaction_list(user):
        return Transaction.objects.filter(account__user=user)

    @staticmethod
    @transaction.atomic
    def transaction_create(user,account,transaction_type,transaction_method,transaction_amount,memo):
        if not account.user ==user:
            raise PermissionDenied('본인 계좌에 대한 거래만 가능합니다')
        if transaction_type == 'DEPOSIT': # 입금이면 +
            account.balance+=transaction_amount
            account.save()
        #     account의 balance를 업데이트하여 account 객체에 저장
        elif transaction_type == 'WITHDRAW': # 지출이면 -
            if transaction_amount > account.balance:
                raise ValidationError('잔액이 부족합니다')
            account.balance-=transaction_amount
            account.save()
        return Transaction.objects.create(
            account=account,
            transaction_type=transaction_type,
            transaction_method=transaction_method,
            transaction_amount=transaction_amount,
            memo=memo
          )
#     객체 생성하면서 업데이트된 account balance를 account에 적용