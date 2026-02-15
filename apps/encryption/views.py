"""
Views for encryption API.
"""
import os
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import HttpResponse, FileResponse
from django.conf import settings

from .serializers import (
    EncryptPDFSerializer,
    DecryptFileSerializer,
    EncryptionResultSerializer,
    TransferHistorySerializer
)
from .services.encryption_orchestrator import EncryptionOrchestrator


class EncryptPDFView(APIView):
    """
    Endpoint to encrypt a PDF file.
    
    POST: Upload PDF, encrypt, and optionally send via email.
    """
    
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        serializer = EncryptPDFSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        pdf_file = serializer.validated_data['pdf_file']
        receiver_email = serializer.validated_data['receiver_email']
        send_email = serializer.validated_data.get('send_email', True)
        
        try:
            # Read PDF bytes
            pdf_bytes = pdf_file.read()
            
            # Encrypt
            orchestrator = EncryptionOrchestrator()
            result = orchestrator.encrypt_pdf(
                pdf_bytes=pdf_bytes,
                original_filename=pdf_file.name,
                sender_email=request.user.email,
                receiver_email=receiver_email,
                send_email=send_email
            )
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DecryptFileView(APIView):
    """
    Endpoint to decrypt an encrypted file.
    
    POST: Upload encrypted file with key, receive decrypted PDF.
    """
    
    permission_classes = [AllowAny]  # Receivers don't need account
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        serializer = DecryptFileSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        encrypted_file = serializer.validated_data['encrypted_file']
        decryption_key = serializer.validated_data['decryption_key']
        
        try:
            # Read encrypted bytes
            encrypted_bytes = encrypted_file.read()
            
            # Decrypt
            orchestrator = EncryptionOrchestrator()
            pdf_bytes, metadata = orchestrator.decrypt_pdf(
                encrypted_bytes=encrypted_bytes,
                decryption_key=decryption_key
            )
            
            # Return PDF as download
            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            original_name = metadata.get('original_filename', 'decrypted.pdf')
            response['Content-Disposition'] = f'attachment; filename="{original_name}"'
            
            return response
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Decryption failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TransferHistoryView(APIView):
    """
    Endpoint to get sender's transfer history.
    
    GET: List all transfers made by the authenticated user.
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            orchestrator = EncryptionOrchestrator()
            transfers = orchestrator.get_sender_history(request.user.email)
            
            serializer = TransferHistorySerializer(transfers, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DownloadEncryptedView(APIView):
    """
    Endpoint to download an encrypted file.
    
    GET: Download encrypted file by filename.
    """
    
    permission_classes = [AllowAny]
    
    def get(self, request, filename):
        try:
            encrypted_path = os.path.join(
                settings.MEDIA_ROOT,
                'encrypted',
                filename
            )
            
            if not os.path.exists(encrypted_path):
                return Response(
                    {'error': 'File not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return FileResponse(
                open(encrypted_path, 'rb'),
                as_attachment=True,
                filename=filename
            )
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
