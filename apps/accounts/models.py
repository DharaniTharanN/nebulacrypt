"""
Custom User model for email-based authentication.
"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import secrets


class UserManager(BaseUserManager):
    """Custom manager for User model with email as the unique identifier."""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom User model using email for authentication."""
    
    username = None
    email = models.EmailField(unique=True, db_index=True)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserManager()
    
    def generate_verification_token(self):
        """Generate a unique verification token for email verification."""
        self.verification_token = secrets.token_urlsafe(32)
        self.save()
        return self.verification_token
    
    def __str__(self):
        return self.email


class AuthToken(models.Model):
    """Simple token model for API authentication."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auth_tokens')
    token = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @classmethod
    def create_token(cls, user):
        """Generate a new auth token for a user."""
        token = secrets.token_urlsafe(32)
        return cls.objects.create(user=user, token=token)
    
    def __str__(self):
        return f"Token for {self.user.email}"
