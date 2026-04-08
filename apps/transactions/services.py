from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError
from apps.transactions.models import Transaction

class TransactionListService:
    @staticmethod
    def transaction_list(user,account=None,transaction_type=None,transaction_amount=None):
        # 기본적으로 user만 인자로 받고 나머지는 기본값으로 None을 할당해 기본 queryset 설정
        queryset = Transaction.objects.filter(account__user=user)

        if account: # account가 입력됬을때 조건추가
            queryset = queryset.filter(account_id=account)
        if transaction_type: # transaction_type가 입력됬을때 조건추가
            queryset = queryset.filter(transaction_type=transaction_type)
        if transaction_amount: # transaction_amount가 입력됬을때 조건추가
            queryset = queryset.filter(transaction_amount__gte=transaction_amount)
        # 최종 queryset 반환
        return queryset

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

class TransactionDetailService:
    @staticmethod
    def transaction_detail(user,pk):
        # Queryset을 반환 하기 때문에 get사용 불가능 filter 사용해야함
        return Transaction.objects.filter(account__user=user,pk=pk)