from django.urls import path
from .views import paystack_webhook

urlpatterns = [
    path('paystack', paystack_webhook, name='paystack-webhook'),
]
