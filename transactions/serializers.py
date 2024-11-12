
from datetime import datetime

from django.core.exceptions import ValidationError
from rest_framework import serializers

from transactions.models import Transaction
from mustard.util import encrypt

class TransactionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'transaction_id',
            'amount',
            'masked_pan',
            'encrypted_pan',
            'encrypted_expiry',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields  # Make all fields read-only

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['card_pan', 'card_expiry', 'card_pin', 'amount']
    
    card_pan = serializers.CharField(write_only=True, min_length=13, max_length=19)
    card_expiry = serializers.CharField(write_only=True)
    card_pin = serializers.CharField(write_only=True, min_length=4, max_length=4)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_card_pan(self, value):
        if not value.isdigit() or len(value) not in [16, 18]:
            raise ValidationError("Card PAN must be 16 or 18 digits.")
        return value

    def validate_card_pin(self, value):
        if not value.isdigit() or len(value) != 4:
            raise ValidationError("Card PIN must be exactly 4 digits.")
        return value
    
    def validate_card_expiry(self, value):
        # Ensure the date format is correct (MM/YY)
        try:
            expiry_date = datetime.strptime(value, "%m/%y")
        except ValueError:
            raise ValidationError("Card expiry date must be in MM/YY format.")
        
        # Get the current date (month and year)
        now = datetime.now()
        current_month = now.month
        current_year = now.year % 100  # Last two digits of the current year

        # Check if the expiry date is in the past
        if (expiry_date.year < now.year) or (expiry_date.year == now.year and expiry_date.month < current_month):
            raise ValidationError("Card expiry date cannot be in the past.")

        return value

    def validate_amount(self, value):
        if value <= 0:
            raise ValidationError("Amount must be greater than 0.")
        return value

    def create(self, validated_data):
        card_pan = validated_data.get("card_pan")
        card_expiry = validated_data.get("card_expiry")
        amount = validated_data.get("amount")

        # Mask the card_pan (show only the last four digits)
        masked_pan = f"************{card_pan[-4:]}"

        # Encrypt card_pan and card_expiry
        encrypted_pan = encrypt(plain_text=card_pan)
        encrypted_expiry = encrypt(plain_text=card_expiry)

        # Save the encrypted and masked data in the database
        transaction = Transaction.objects.create(
            masked_pan=masked_pan,
            encrypted_pan=encrypted_pan,
            encrypted_expiry=encrypted_expiry,
            amount=amount
        )

        return transaction
