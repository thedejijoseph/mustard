from rest_framework import serializers
from .models import Wallet

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
