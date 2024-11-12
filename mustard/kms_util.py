
import base64
import logging
import requests

from django.conf import settings
from rest_framework.exceptions import APIException
from requests.exceptions import RequestException

from environs import Env

env = Env()
env.read_env()

# Configure logging
logger = logging.getLogger(__name__)

# Constants (ensure these are set in Django settings)
INF_CLIENT_SECRET = env.str('INF_CLIENT_SECRET')
INF_CLIENT_ID = env.str('INF_CLIENT_ID')
INF_KMS_KEY_ID = env.str('INF_KMS_KEY_ID')
INFISICAL_BASE_URL = "https://app.infisical.com/api/v1"

class InfisicalKMSClient:
    def __init__(self):
        self.access_token = None
        self.token_type = None

    def authenticate(self):
        """Authenticate with Infisical API and retrieve access token."""
        auth_url = f"{INFISICAL_BASE_URL}/auth/universal-auth/login"
        data = {
            "clientSecret": INF_CLIENT_SECRET,
            "clientId": INF_CLIENT_ID
        }

        try:
            response = requests.post(auth_url, data=data)
            response.raise_for_status()
            auth_data = response.json()
            self.access_token = auth_data.get("accessToken")
            self.token_type = auth_data.get("tokenType")

            logger.info("Authentication successful")
            return self.access_token
        except RequestException as e:
            logger.error(f"Authentication failed: {e}")
            raise APIException("Authentication with Infisical KMS failed")

    def _get_headers(self):
        """Get authorization headers for requests."""
        if not self.access_token:
            self.authenticate()
        return {"Authorization": f"{self.token_type} {self.access_token}"}

    def encrypt(self, plaintext):
        """Encrypt data using Infisical KMS."""
        encrypt_url = f"{INFISICAL_BASE_URL}/kms/keys/{INF_KMS_KEY_ID}/encrypt"
        plaintext_b64 = base64.b64encode(plaintext.encode("utf-8")).decode("utf-8")
        data = {"plaintext": plaintext_b64}

        try:
            response = requests.post(encrypt_url, json=data, headers=self._get_headers())
            response.raise_for_status()
            encrypted_data = response.json().get("ciphertext")

            logger.info(f"Encryption request successful for key ID {INF_KMS_KEY_ID}")
            return encrypted_data
        except RequestException as e:
            logger.error(f"Encryption failed: {e}")
            raise APIException("Failed to encrypt data with Infisical KMS")

    def decrypt(self, ciphertext):
        """Decrypt data using Infisical KMS."""
        decrypt_url = f"{INFISICAL_BASE_URL}/kms/keys/{INF_KMS_KEY_ID}/decrypt"
        data = {"ciphertext": ciphertext}

        try:
            response = requests.post(decrypt_url, json=data, headers=self._get_headers())
            response.raise_for_status()
            decrypted_data_b64 = response.json().get("plaintext")
            decrypted_data = base64.b64decode(decrypted_data_b64).decode("utf-8")

            logger.info(f"Decryption request successful for key ID {INF_KMS_KEY_ID}")
            return decrypted_data
        except RequestException as e:
            logger.error(f"Decryption failed: {e}")
            raise APIException("Failed to decrypt data with Infisical KMS")
