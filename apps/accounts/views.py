"""
Views for user authentication.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.mail import send_mail
from django.conf import settings

from .models import User, AuthToken
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer


class RegisterView(APIView):
    """User registration endpoint."""
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate verification token
            token = user.generate_verification_token()
            
            # Send verification email
            verification_url = f"{settings.CORS_ALLOWED_ORIGINS[0]}/verify/{token}"
            
            try:
                send_mail(
                    subject='Verify your email - PDF Encryption System',
                    message=f'Click the link to verify your email: {verification_url}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            except Exception as e:
                # For development, just mark as verified
                if settings.DEBUG:
                    user.is_verified = True
                    user.save()
            
            return Response({
                'message': 'Registration successful. Please check your email for verification.',
                'email': user.email,
                'verified': user.is_verified
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    """Email verification endpoint."""
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        token = request.data.get('token')
        
        if not token:
            return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(verification_token=token)
            user.is_verified = True
            user.verification_token = None
            user.save()
            
            return Response({'message': 'Email verified successfully'})
        except User.DoesNotExist:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """User login endpoint."""
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Create auth token
            auth_token = AuthToken.create_token(user)
            
            return Response({
                'token': auth_token.token,
                'user': UserSerializer(user).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """User logout endpoint."""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Delete the current token
        if hasattr(request, 'auth') and request.auth:
            request.auth.delete()
        
        return Response({'message': 'Logged out successfully'})


class ProfileView(APIView):
    """User profile endpoint."""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response(UserSerializer(request.user).data)
    
    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
