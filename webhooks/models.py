from django.db import models

class WebhookLog(models.Model):
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Webhook: {self.event_type} at {self.received_at}"
