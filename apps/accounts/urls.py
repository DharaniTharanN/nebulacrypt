"""
URL configuration for accounts app.
"""
from django.urls import path
from .views import RegisterView, LoginView, LogoutView, VerifyEmailView, ProfileView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('verify/', VerifyEmailView.as_view(), name='verify-email'),
    path('profile/', ProfileView.as_view(), name='profile'),
]
