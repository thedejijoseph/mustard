from rest_framework import serializers
from .models import Wallet, Transaction

class CreateWalletSerializer(serializers.ModelSerializer):
    currency = serializers.ChoiceField(choices=Wallet.CURRENCY_CHOICES)

    class Meta:
        model = Wallet
        fields = ['currency']

class FundWalletSerializer(serializers.Serializer):
    email = serializers.EmailField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)

class WithdrawSerializer(serializers.Serializer):
    account_number = serializers.CharField(max_length=10)
    bank_code = serializers.CharField(max_length=3)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    reason = serializers.CharField(max_length=255, required=False)

class TransferSerializer(serializers.Serializer):
    recipient_wallet_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['wallet_id', 'currency', 'balance', 'created_at']
    
    def validate(self, attrs):
        user = attrs["user"]
        currency = attrs["currency"]
        if Wallet.objects.filter(user=user, currency=currency).exists():
            raise serializers.ValidationError(f"A wallet for {currency} already exists.")
        return attrs


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'transaction_id',
            'wallet',
            'amount',
            'transaction_type',
            'recipient',
            'status',
            'created_at',
        ]
    
    def validate(self, attrs):
        credit_source_type = attrs.get("credit_source_type")
        credit_source_id = attrs.get("credit_source_id")
        debit_destination_type = attrs.get("debit_destination_type")
        debit_destination_id = attrs.get("debit_destination_id")

        if credit_source_type and not credit_source_id:
            raise serializers.ValidationError("Credit source ID is required when specifying a credit source.")
        if debit_destination_type and not debit_destination_id:
            raise serializers.ValidationError("Debit destination ID is required when specifying a debit destination.")
        return attrs
