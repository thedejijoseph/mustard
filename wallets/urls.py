from django.urls import path
from .views import CreateWalletView,FundWalletView, WithdrawView, TransferView, \
    UserWalletsView, WalletDetailView, WalletTransactionHistoryView

urlpatterns = [
    path('create/', CreateWalletView.as_view(), name='create_wallet'),
    path('', UserWalletsView.as_view(), name='user-wallets'),
    path('<uuid:wallet_id>', WalletDetailView.as_view(), name='wallet-detail'),
    path('<uuid:wallet_id>/transactions', WalletTransactionHistoryView.as_view(), name='wallet-transactions'),
    path('fund', FundWalletView.as_view(), name='fund_wallet'),
    path('withdraw/', WithdrawView.as_view(), name='withdraw'),
    path('transfer/', TransferView.as_view(), name='transfer'),
]
