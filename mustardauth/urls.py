from django.urls import path
from .views import CreateUserView, LoginView, PasswordResetInitiateView, PasswordResetCompleteView

urlpatterns = [
    path('create/basic', CreateUserView.as_view(), name='create_user'),
    path('login/basic', LoginView.as_view(), name='login_user'),
    path('reset-password/initiate', PasswordResetInitiateView.as_view(), name='password_reset_initiate'),
    path('reset-password/complete', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
