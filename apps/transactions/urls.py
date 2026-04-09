from django.urls import path

from apps.transactions.views import TransactionDetailView, TransactionListView

app_name = "transaction"

urlpatterns = [
    path("",TransactionListView.as_view(),name="list"),
    path("<int:transaction_pk>/",TransactionDetailView.as_view(),name="detail"),
]