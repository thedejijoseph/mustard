from django.urls import path
from .views import CreateWalletView,FundWalletView, WithdrawFundsView, WalletTransferView, \
    UserWalletsView, WalletDetailView, WalletTransactionHistoryView, UsersWalletsView

urlpatterns = [
    path('create', CreateWalletView.as_view(), name='create_wallet'),
    path('fund', FundWalletView.as_view(), name='fund_wallet'),
    path('withdraw', WithdrawFundsView.as_view(), name='withdraw'),
    path('transfer', WalletTransferView.as_view(), name='transfer'),
    path('<uuid:wallet_id>', WalletDetailView.as_view(), name='wallet-detail'),
    path('<uuid:wallet_id>/transactions', WalletTransactionHistoryView.as_view(), name='wallet-transactions'),
    path('', UserWalletsView.as_view(), name='user-wallets'),
    path('<str:username>', UsersWalletsView.as_view(), name="user_wallets"),
]
