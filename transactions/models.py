from django.db import models
from django.utils import timezone

import uuid

class Transaction(models.Model):
    uid = models.AutoField(primary_key=True)
    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    masked_pan = models.CharField(max_length=18)
    encrypted_pan = models.CharField()
    encrypted_expiry = models.CharField()
    amount = models.FloatField()
