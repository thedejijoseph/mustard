from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.db.models import JSONField
import uuid

User = get_user_model()

class Wallet(models.Model):
    CURRENCY_CHOICES = [
        ('NGN', 'Nigerian Naira'),
        ('USD', 'US Dollar'),
    ]

    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    # user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallet")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wallets")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='NGN')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "currency")  # Ensure one wallet per currency per user
    
    def __str__(self):
        return f"{self.user.email}'s Wallet - {self.currency}"
class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('debit', 'Debit'),
        ('credit', 'Credit'),
    ]
    TRANSACTION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    status = models.CharField(max_length=10, choices=TRANSACTION_STATUS_CHOICES, default='pending')
    payment_provider = models.CharField(max_length=50, null=True, blank=True)
    reference = models.CharField(max_length=100, unique=True, null=True, blank=True)
    recipient = models.ForeignKey(
        Wallet, null=True, blank=True, on_delete=models.SET_NULL, related_name="received_transfers"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = JSONField(default=dict, blank=True)

    # Credit source and debit destination
    credit_source_type = models.CharField(max_length=50, null=True, blank=True)  # e.g., "wallet", "card"
    credit_source_id = models.CharField(max_length=50, null=True, blank=True)  # e.g., wallet_id, card_id
    debit_destination_type = models.CharField(max_length=50, null=True, blank=True)  # e.g., "bankaccount", "wallet"
    debit_destination_id = models.CharField(max_length=50, null=True, blank=True)  # e.g., bankaccount_id, wallet_id

    def __str__(self):
        return f"{self.transaction_type} - {self.amount}"
