from rest_framework import serializers

from apps.transactions.models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    transaction_type_display = serializers.CharField(
        source="get_transaction_type_display",read_only=True
    )
    transaction_method_display = serializers.CharField(
        source="get_transaction_method_display",read_only=True
    )
    class Meta:
        model = Transaction
        fields = [
            "id",
            "account",
            "transaction_type",
            "transaction_type_display",
            # 응답용 transaction_type
            "transaction_method",
            "transaction_method_display",
            # 응답용 transaction_method
            "transaction_amount",
            "balance_after",
            "memo",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id","created_at","updated_at","balance_after"]

    def validate_transaction_amount(self,value):
        if value <= 0:
            raise serializers.ValidationError("거래금액은 0보다 커야합니다")
        return value