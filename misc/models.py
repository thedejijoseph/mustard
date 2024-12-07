
from django.db import models
from django.utils.timezone import now

import logging

logger = logging.getLogger(__name__)

class OTP(models.Model):
    email = models.EmailField()
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=now)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        logger.info(f"Generated OTP for {self.email}: {self.otp_code}")
        super().save(*args, **kwargs)