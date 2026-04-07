from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSet

from apps.transactions.models import Transaction
from apps.transactions.serializers import TransactionSerializer


class TransactionList(generics.ListCreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
       return Transaction.objects.filter(account__user=self.request.user).order_by('account_id')

class TransactionDetail(generics.RetrieveUpdateDestroyAPIView):
    ...

