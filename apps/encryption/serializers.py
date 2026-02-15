"""
Serializers for encryption API.
"""
from rest_framework import serializers


class EncryptPDFSerializer(serializers.Serializer):
    """Serializer for PDF encryption request."""
    
    pdf_file = serializers.FileField()
    receiver_email = serializers.EmailField()
    send_email = serializers.BooleanField(default=True)
    
    def validate_pdf_file(self, value):
        """Validate that the uploaded file is a PDF."""
        if not value.name.lower().endswith('.pdf'):
            raise serializers.ValidationError("Only PDF files are allowed")
        
        # Check file size (max 50MB)
        max_size = 50 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError("File size must be less than 50MB")
        
        return value


class DecryptFileSerializer(serializers.Serializer):
    """Serializer for file decryption request."""
    
    encrypted_file = serializers.FileField()
    decryption_key = serializers.CharField(max_length=500)
    
    def validate_encrypted_file(self, value):
        """Validate the encrypted file."""
        if not value.name.lower().endswith('.png'):
            raise serializers.ValidationError("Invalid encrypted file format. Expected .png")
        return value


class EncryptionResultSerializer(serializers.Serializer):
    """Serializer for encryption result."""
    
    success = serializers.BooleanField()
    transfer_id = serializers.CharField()
    timestamp = serializers.CharField()
    num_pages = serializers.IntegerField()
    encrypted_file = serializers.CharField()
    decryption_key = serializers.CharField()
    email_sent = serializers.BooleanField()


from .models import EncryptionTransfer


class TransferHistorySerializer(serializers.ModelSerializer):
    """Serializer for transfer history."""
    
    transfer_id = serializers.IntegerField(source='id')
    
    class Meta:
        model = EncryptionTransfer
        fields = ['transfer_id', 'receiver_email', 'original_filename', 'timestamp']
