
import logging

from django.shortcuts import render

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from transactions.models import Transaction
from transactions.serializers import TransactionSerializer, TransactionDetailSerializer

transaction_logger = logging.getLogger('transaction_logger')

class TransactionView(APIView):
    def get(self, request):
        transactions = Transaction.objects.all()
        serializer = TransactionDetailSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            transaction = serializer.save()

            transaction_details = {
                'masked_pan': transaction.masked_pan,
                'amount': transaction.amount,
                'status': 'Success',
                'timestamp': transaction.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            transaction_logger.info(f"Transaction processed: {transaction_details}")

            return Response(
                {
                    "message": "Transaction processed", 
                    "transaction_id": transaction.transaction_id
                }, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
