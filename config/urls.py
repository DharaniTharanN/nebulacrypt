"""
URL configuration for PDF Encryption System.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'auth': reverse('accounts-root', request=request, format=format),
        'encryption': reverse('encrypt-pdf', request=request, format=format), # Pointing to a known endpoint for now or root of that app
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api_root, name='api-root'),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/encryption/', include('apps.encryption.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
