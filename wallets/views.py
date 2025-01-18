
from decimal import Decimal, ROUND_DOWN, InvalidOperation

from django.shortcuts import render
from django.utils.timezone import now
from django.db.models import Sum
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework import status

from .serializers import WithdrawSerializer, TransferSerializer, \
    WalletSerializer, TransactionSerializer
from .payment_providers import PaystackProvider

from .models import Wallet, Transaction
from bankaccounts.models import BankAccount

class UserWalletsView(APIView):
    """Fetch all wallets belonging to the signed-in user."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        wallets = Wallet.objects.filter(user=user)
        serializer = WalletSerializer(wallets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class WalletDetailView(APIView):
    """Fetch details of a specific wallet."""
    permission_classes = [IsAuthenticated]

    def get(self, request, wallet_id):
        user = request.user
        try:
            wallet = Wallet.objects.get(wallet_id=wallet_id, user=user)
        except Wallet.DoesNotExist:
            return Response(
                {"error": "Wallet not found or you are not authorised to access this wallet."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = WalletSerializer(wallet)
        return Response(serializer.data, status=status.HTTP_200_OK)

class WalletTransactionHistoryView(APIView):
    """Fetch transaction history for a specific wallet."""
    permission_classes = [IsAuthenticated]

    def get(self, request, wallet_id):
        user = request.user
        try:
            wallet = Wallet.objects.get(wallet_id=wallet_id, user=user)
        except Wallet.DoesNotExist:
            return Response(
                {"error": "Wallet not found or you are not authorised to access this wallet."},
                status=status.HTTP_404_NOT_FOUND
            )

        transactions = Transaction.objects.filter(wallet=wallet).order_by('-created_at')
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CreateWalletView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        currency = request.data.get("currency")

        # Temporary filter: only allow NGN wallets
        if currency != "NGN":
            return Response(
                {"error": "Only NGN wallets can be created at the moment."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if hasattr(user, 'wallet'):
            return Response(
                {"error": "User already has a wallet."},
                status=status.HTTP_400_BAD_REQUEST
            )

        wallet = Wallet.objects.create(user=user, currency=currency)
        return Response(
            {
                "wallet_id": wallet.wallet_id,
                "currency": wallet.currency,
                "balance": wallet.balance,
                "created_at": wallet.created_at,
            },
            status=status.HTTP_201_CREATED
        )
class FundWalletView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        wallet_id = request.data.get("wallet_id")
        amount = request.data.get("amount")

        # Validate wallet
        try:
            wallet = Wallet.objects.get(wallet_id=wallet_id)
        except Wallet.DoesNotExist:
            return Response({"error": "Wallet not found."}, status=status.HTTP_404_NOT_FOUND)

        if wallet.user != user:
            return Response({"error": "You are not authorised to fund this wallet."}, status=status.HTTP_403_FORBIDDEN)

        # Validate amount
        try:
            amount = Decimal(amount).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
            if amount <= 0:
                raise ValueError
        except (TypeError, ValueError):
            return Response({"error": "Invalid amount."}, status=status.HTTP_400_BAD_REQUEST)


        # Fetch user's transaction limits
        transaction_limits = user.transaction_limits
        daily_limit = transaction_limits["credit_limit"]
        max_balance = transaction_limits["max_balance"]

        # Check daily credit limit
        today = now().date()
        daily_credit_total = Transaction.objects.filter(
            wallet=wallet,
            transaction_type="credit",
            created_at__date=today
        ).aggregate(total=Sum('amount'))['total'] or Decimal("0.00")

        if daily_credit_total + amount > daily_limit:
            return Response(
                {"error": "Daily credit limit exceeded."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check max account balance
        if max_balance is not None and wallet.balance + amount > max_balance:
            return Response(
                {"error": "Maximum account balance limit exceeded."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Initiate payment provider
        payment_provider = PaystackProvider()
        payment_response = payment_provider.initiate_payment(float(amount), wallet.user.email)

        if payment_response.get("status") and payment_response["data"]:
            authorization_url = payment_response["data"]["authorization_url"]
            reference = payment_response["data"]["reference"]

            # Create pending transaction
            Transaction.objects.create(
                wallet=wallet,
                amount=amount,
                transaction_type="credit",
                status="pending",
                payment_provider="paystack",
                reference=reference,
            )

            return Response(
                {"status": "success", "message": "Payment initiated.", "authorization_url": authorization_url},
                status=status.HTTP_200_OK,
            )

        return Response({"error": "Failed to initiate payment."}, status=status.HTTP_400_BAD_REQUEST)

class WithdrawFundsView(APIView):
    def post(self, request, *args, **kwargs):
        user = request.user
        wallet = user.wallet

        # Extract and validate input
        amount = request.data.get("amount")
        currency = request.data.get("currency", "NGN")
        bank_account_id = request.data.get("bank_account_id")

        # Ensure all required fields are provided
        if not amount or not bank_account_id:
            return Response(
                {"error": "Amount and bank account ID are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate amount
        try:
            amount = Decimal(amount).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
            if amount <= 0:
                raise ValueError("Amount must be greater than 0.")
        except (ValueError, InvalidOperation) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch bank account
        bank_account = get_object_or_404(BankAccount, id=bank_account_id, user=user)

        # Validate transaction against user's tier limits
        limits = user.transaction_limits
        if amount > Decimal(limits["debit_limit"]):
            return Response(
                {"error": f"Amount exceeds your tier's debit limit of {limits['debit_limit']}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if wallet.balance - amount < 0:
            return Response(
                {"error": "Insufficient wallet balance."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Call payment provider to transfer funds
        provider = PaystackProvider()
        try:
            response = provider.transfer_funds(
                amount=float(amount),  # Convert Decimal to float for API
                recipient_code=bank_account.recipient_code,
                reason="Wallet withdrawal",
            )
        except Exception as e:
            return Response(
                {"error": "Withdrawal failed", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Log the transaction
        transaction = Transaction.objects.create(
            wallet=wallet,
            amount=amount,
            transaction_type="debit",
            recipient=None,  # No wallet recipient in this case
            metadata={"bank_account": str(bank_account.id)},
            debit_destination_type="bankaccount",
            debit_destination_id=str(bank_account.id),
        )

        # Update wallet balance
        wallet.balance -= amount
        wallet.save()

        return Response(
            {"message": "Withdrawal successful", "transaction_id": transaction.transaction_id, "reference": response.get("data", {}).get("reference")},
            status=status.HTTP_200_OK,
        )

class TransferView(APIView):
    def post(self, request):
        serializer = TransferSerializer(data=request.data)
        if serializer.is_valid():
            recipient_wallet_id = serializer.validated_data['recipient_wallet_id']
            amount = serializer.validated_data['amount']

            wallet = request.user.wallet
            if wallet.balance < amount:
                return Response({"error": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                recipient_wallet = Wallet.objects.get(pk=recipient_wallet_id)
            except Wallet.DoesNotExist:
                return Response({"error": "Recipient wallet not found"}, status=status.HTTP_404_NOT_FOUND)

            # Perform transfer
            wallet.balance -= amount
            recipient_wallet.balance += amount
            wallet.save()
            recipient_wallet.save()

            Transaction.objects.create(wallet=wallet, amount=amount, transaction_type="TRANSFER", recipient=recipient_wallet)
            return Response({"status": "Transfer successful"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
