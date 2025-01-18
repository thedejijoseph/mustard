from rest_framework import serializers
from .models import BankAccount

class AddBankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = ["bank_code", "account_number"]
        extra_kwargs = {
            "bank_code": {"required": True, "max_length": 10},
            "account_number": {"required": True},
        }

class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = ["id", "bank_name", "account_number", "account_name", "bank_code", "recipient_code", "created_at"]
        read_only_fields = ["id", "account_name", "recipient_code", "created_at"]

    def validate_account_number(self, value):
        if not value.isdigit() or len(value) < 10:
            raise serializers.ValidationError("Invalid account number.")
        return value

    def validate_bank_code(self, value):
        if not value.isdigit() or len(value) != 3:
            raise serializers.ValidationError("Invalid bank code.")
        return value
