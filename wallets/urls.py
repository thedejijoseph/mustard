from django.urls import path
from .views import CreateWalletView,FundWalletView, WithdrawView, TransferView

urlpatterns = [
    path('create/', CreateWalletView.as_view(), name='create_wallet'),
    path('fund', FundWalletView.as_view(), name='fund_wallet'),
    path('withdraw/', WithdrawView.as_view(), name='withdraw'),
    path('transfer/', TransferView.as_view(), name='transfer'),
]
