from decimal import Decimal

from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated

from apps.transactions.models import Transaction


class CustomPermissionService(IsAuthenticated):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):  # GET요청 또는 로그인한 유저
            return False
        if check_staff(request):
            # staff인지 만일 staff면 GET요청이 아니면 False
            if check_superuser(request):
                # superuser는 is_staff랑 is_superuser가 둘다 True
                return True
            if not check_method(request):
                # staff가 참일때는 get만 가능하도록
                return False
            return True
        return True


def check_staff(request):
    return bool(request.user.is_staff)


def check_superuser(request):
    return bool(request.user.is_superuser)


def check_method(request):
    return bool(request.method in SAFE_METHODS)


class TransactionListService:
    @staticmethod
    def transaction_list(
        user, account=None, transaction_type=None, transaction_amount=None
    ):
        if user.is_superuser:
            queryset = Transaction.objects.all()
        else:
            queryset = Transaction.objects.filter(user=user)

        # # 1. 기본 쿼리셋 설정
        # if user.is_superuser:
        #     queryset = Transaction.objects.all()
        # else:
        #     queryset = Transaction.objects.filter(
        #         Q(account__user=user) | Q(account__isnull=True)
        #     )
        if account:
            if account == "0":
                queryset = queryset.filter(account__isnull=True)
            else:
                queryset = queryset.filter(account_id=account)
        if transaction_type:  # transaction_type가 입력됬을때 조건추가
            queryset = queryset.filter(transaction_type=transaction_type)
        if transaction_amount:  # transaction_amount가 입력됬을때 조건추가
            queryset = queryset.filter(transaction_amount__gte=transaction_amount)
        # 최종 queryset 반환
        return queryset

    @staticmethod
    @transaction.atomic
    def transaction_create(user, transaction_data):
        account_val = transaction_data["account"]
        if isinstance(account_val, int):
            from apps.accounts.models import Account

            account = Account.objects.get(id=account_val)
        else:
            account = account_val
        transaction_type = transaction_data["transaction_type"]
        transaction_method = transaction_data["transaction_method"]
        transaction_amount = Decimal(str(transaction_data["transaction_amount"]))
        memo = transaction_data.get("memo", "")
        # validated_data.get("memo","")로 수정해야 memo가 blank일때 에러를 방지할수 있다
        # services에서 정의한 transaction_create을 활용하기 전 변수 설정
        if not account.user == user:
            raise PermissionDenied("본인 계좌에 대한 거래만 가능합니다")
        if transaction_type == "DEPOSIT":  # 입금이면 +
            account.balance += transaction_amount
            account.save()
        #     account의 balance를 업데이트하여 account 객체에 저장
        elif transaction_type == "WITHDRAW":  # 지출이면 -
            if transaction_amount > account.balance:
                raise ValidationError("잔액이 부족합니다")
            account.balance -= transaction_amount
            account.save()
        return Transaction.objects.create(
            account=account,
            user=user,
            transaction_type=transaction_type,
            transaction_method=transaction_method,
            transaction_amount=transaction_amount,
            balance_after=account.balance,
            memo=memo,
        )


#     객체 생성하면서 업데이트된 account balance를 account에 적용


class TransactionDetailService:
    @staticmethod
    def transaction_detail(user):
        queryset = Transaction.objects.filter(user=user)
        if user.is_superuser:
            queryset = Transaction.objects.all()
        # Queryset을 반환 하기 때문에 get사용 불가능 filter 사용해야함
        return queryset

    @staticmethod
    @transaction.atomic
    def transaction_delete(instance):
        from apps.accounts.models import Account

        if instance.account:
            account = Account.objects.get(id=instance.account.id)
            if instance.transaction_type == "DEPOSIT":
                amount = instance.transaction_amount
                account.balance -= amount
            else:
                amount = instance.transaction_amount
                account.balance += amount
            account.save()
        instance.delete()
