from django.urls import path
from apps.transactions.views import TransactionListView,TransactionDetailView

app_name = 'transaction'

urlpatterns = [
    path('transactions/',TransactionListView.as_view(),name='list'),
    path('transactions/<int:pk>/',TransactionDetailView.as_view(),name='detail'),
]