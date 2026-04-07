from rest_framework import request

from apps.transactions.serializers import TransactionSerializer
from apps.transactions.views import TransactionList


def transaction_list()