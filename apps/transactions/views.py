from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.transactions.models import Transaction
from apps.transactions.serializers import TransactionSerializer
from apps.transactions.services import TransactionListService


class TransactionListView(generics.ListCreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
       return TransactionListService.transaction_list(self.request.user)

    def perform_create(self,serializer):
        user = self.request.user
        account = serializer.validated_data['account']
        transaction_type = serializer.validated_data['transaction_type']
        transaction_method = serializer.validated_data['transaction_method']
        transaction_amount = serializer.validated_data['transaction_amount']
        memo = serializer.validated_data['memo']
        result = TransactionListService.transaction_create(user,account,transaction_type,transaction_method,transaction_amount,memo)
        serializer.instance = result

class TransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return TransactionListService.transaction_list(self.request.user)