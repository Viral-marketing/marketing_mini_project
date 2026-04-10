from rest_framework import serializers

from .models import Account


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["id", "account_number", "bank_code", "account_type", "balance"]
        read_only_fields = ["id"]

    def validate_balance(self, value):
        if value < 0:
            raise serializers.ValidationError("잔액은 0보다 커야합니다")
        return value
