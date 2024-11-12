
from django.urls import path
from . import views

urlpatterns = [
    path('transactions', views.TransactionView.as_view()),
    path('processTransaction', views.TransactionView.as_view()),
]