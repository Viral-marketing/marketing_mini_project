from rest_framework import serializers

from .models import Account


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["id", "account_number", "bank_code", "account_type", "balance"]
        read_only_fields = ["id"]
