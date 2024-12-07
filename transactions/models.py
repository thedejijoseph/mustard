from django.db import models
from django.utils import timezone

import uuid

class Transaction(models.Model):
    uid = models.AutoField(primary_key=True)
    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    masked_pan = models.CharField(max_length=18)
    encrypted_pan = models.TextField()
    encrypted_expiry = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

class TransactionArchive(models.Model):
    uid = models.AutoField(primary_key=True)
    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    masked_pan = models.CharField(max_length=18)
    encrypted_pan = models.TextField()
    encrypted_expiry = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
