import requests
from abc import ABC, abstractmethod
from django.conf import settings

class PaymentProviderInterface(ABC):
    """Abstract Base Class for Payment Providers"""

    @abstractmethod
    def initiate_payment(self, amount, email, metadata=None):
        """Initiate a payment request"""
        pass

    @abstractmethod
    def transfer_funds(self, account_number, bank_code, amount, reason=""):
        """Transfer funds to a bank account"""
        pass

class PaystackProvider(PaymentProviderInterface):
    BASE_URL = "https://api.paystack.co"

    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY

    def _headers(self):
        return {"Authorization": f"Bearer {self.secret_key}"}

    def initiate_payment(self, amount, email, metadata=None):
        url = f"{self.BASE_URL}/transaction/initialize"
        payload = {
            "email": email,
            "amount": int(amount * 100),  # Convert to kobo
            "metadata": metadata or {}
        }
        response = requests.post(url, json=payload, headers=self._headers())
        response.raise_for_status()
        return response.json()

    def transfer_funds(self, account_number, bank_code, amount, reason=""):
        url = f"{self.BASE_URL}/transfer"
        payload = {
            "source": "balance",
            "amount": int(amount * 100),  # Convert to kobo
            "recipient": {
                "type": "nuban",
                "account_number": account_number,
                "bank_code": bank_code,
                "currency": "NGN",
            },
            "reason": reason,
        }
        response = requests.post(url, json=payload, headers=self._headers())
        response.raise_for_status()
        return response.json()
