from django.urls import path
from .views import AddBankAccountView

urlpatterns = [
    path('add', AddBankAccountView.as_view(), name='add-bank-account'),
]
