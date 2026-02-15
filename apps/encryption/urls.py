"""
URL configuration for encryption app.
"""
from django.urls import path
from .views import (
    EncryptPDFView,
    DecryptFileView,
    TransferHistoryView,
    DownloadEncryptedView
)

urlpatterns = [
    path('encrypt/', EncryptPDFView.as_view(), name='encrypt-pdf'),
    path('decrypt/', DecryptFileView.as_view(), name='decrypt-file'),
    path('history/', TransferHistoryView.as_view(), name='transfer-history'),
    path('download/<str:filename>/', DownloadEncryptedView.as_view(), name='download-encrypted'),
]
