
import json
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from wallets.models import Wallet, Transaction
from .models import WebhookLog


@csrf_exempt
def paystack_webhook(request):
    if request.method == "POST":
        try:
            # Log webhook payload
            payload = json.loads(request.body)
            event_type = payload.get("event", "unknown")
            WebhookLog.objects.create(event_type=event_type, payload=payload)

            if event_type == "charge.success":
                data = payload.get("data", {})

                # Extract payment details
                reference = data.get("reference")
                amount = Decimal(data.get("amount", 0)) / 100  # Convert kobo to naira

                try:
                    transaction = Transaction.objects.get(reference=reference)

                    # Crosscheck amount
                    if transaction.amount != amount:
                        return JsonResponse({"error": "Amount mismatch."}, status=400)

                    # Update transaction and wallet
                    transaction.status = "COMPLETED"
                    transaction.save()

                    transaction.wallet.balance += transaction.amount
                    transaction.wallet.save()

                    return JsonResponse({"status": "success"}, status=200)
                except Transaction.DoesNotExist:
                    return JsonResponse({"error": "Transaction not found."}, status=404)

            return JsonResponse({"error": "Unsupported event type."}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)
