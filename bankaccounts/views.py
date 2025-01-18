
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .serializers import AddBankAccountSerializer
from .models import BankAccount
from wallets.payment_providers import PaystackProvider


class AddBankAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = AddBankAccountSerializer(data=request.data)
        if serializer.is_valid():
            bank_code = serializer.validated_data["bank_code"]
            account_number = serializer.validated_data["account_number"]

            # Call the payment provider to resolve account details
            provider = PaystackProvider()
            try:
                response = provider.resolve_bank_account(account_number, bank_code)
                account_name = response["account_name"]
            except Exception as e:
                return Response(
                    {"error": "Failed to resolve bank account details", "details": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Call the payment provider to create a transfer recipient
            try:
                recipient_response = provider.create_transfer_recipient(
                    account_number=account_number,
                    bank_code=bank_code,
                    account_name=account_name,
                )
                recipient_code = recipient_response["recipient_code"]
                bank_name = recipient_response["details"]["bank_name"]
            except Exception as e:
                return Response(
                    {"error": "Failed to create transfer recipient", "details": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Save the bank account details
            bank_account = BankAccount.objects.create(
                user=request.user,
                bank_name=bank_name,
                account_number=account_number,
                account_name=account_name,
                bank_code=bank_code,
                recipient_code=recipient_code,
            )

            return Response(
                {
                    "message": "Bank account added successfully",
                    "bank_account": {
                        "id": str(bank_account.id),
                        "bank_name": bank_account.bank_name,
                        "account_number": bank_account.account_number,
                        "account_name": bank_account.account_name,
                    },
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    