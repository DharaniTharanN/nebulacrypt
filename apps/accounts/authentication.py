"""
Custom token authentication for REST API.
"""
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import AuthToken


class TokenAuthentication(BaseAuthentication):
    """Token-based authentication using Bearer token."""
    
    keyword = 'Bearer'
    
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith(f'{self.keyword} '):
            return None
        
        token = auth_header[len(self.keyword) + 1:]
        
        try:
            auth_token = AuthToken.objects.select_related('user').get(token=token)
            return (auth_token.user, auth_token)
        except AuthToken.DoesNotExist:
            raise AuthenticationFailed('Invalid token')
