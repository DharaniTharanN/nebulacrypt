"""
Encryption Orchestrator Service.
Coordinates the entire PDF encryption/decryption workflow.
"""
import os
import tempfile
import secrets
import base64
import io
from datetime import datetime
from typing import Tuple, Optional
from PIL import Image

from .pdf_processor import PDFProcessor
from .pixel_processor import PixelProcessor
from .dckp_es import DCKPESEncryptor, create_encryption_package, extract_encryption_package
from apps.encryption.models import EncryptionTransfer
from .email_service import EmailService

from django.conf import settings


class EncryptionOrchestrator:
    """
    Orchestrates the complete PDF encryption workflow:
    1. PDF -> Images
    2. Pixel chunking (32px)
    3. Shuffle with key
    4. DCKP-ES encryption
    5. Package and save
    6. Send via email
    """
    
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.pixel_processor = PixelProcessor()
        self.email_service = EmailService()
        self.media_root = getattr(settings, 'MEDIA_ROOT', 'media')
    
    def encrypt_pdf(
        self,
        pdf_bytes: bytes,
        original_filename: str,
        sender_email: str,
        receiver_email: str,
        send_email: bool = True
    ) -> dict:
        """
        Encrypt a PDF file using DCKP-ES algorithm.
        
        Workflow:
        1. Convert PDF to images
        2. For each image:
           - Chunk into 32-pixel blocks
           - Shuffle chunks
           - Apply DCKP-ES encryption
        3. Package encrypted data with metadata
        4. Record transfer in MongoDB
        5. Optionally send via email
        
        Args:
            pdf_bytes: PDF file as bytes
            original_filename: Original filename
            sender_email: Sender's email
            receiver_email: Receiver's email
            send_email: Whether to send via email
            
        Returns:
            dict with encryption results
        """
        timestamp = datetime.utcnow()
        
        # Initialize encryptor with filename and timestamp
        encryptor = DCKPESEncryptor(original_filename, timestamp)
        shuffle_seed = encryptor._get_shuffle_seed()
        
        # Step 1: Convert PDF to images
        images = self.pdf_processor.pdf_to_images(pdf_bytes=pdf_bytes)
        num_pages = len(images)
        
        # Previews for visualization (list of dicts, one per page)
        previews = []

        encrypted_images = []
        metadata_list = []
        shuffle_indices_list = []
        
        # Step 2-4: Process each page
        for page_num, image in enumerate(images):
            page_previews = {'page': page_num + 1}
            
            # Original Preview
            try:
                buffered = io.BytesIO()
                image.save(buffered, format="JPEG")
                page_previews['original'] = f"data:image/jpeg;base64,{base64.b64encode(buffered.getvalue()).decode('utf-8')}"
            except Exception:
                page_previews['original'] = ""

            # Chunk pixels
            chunks, metadata = self.pixel_processor.chunk_pixels(image)
            
            # Capture Chunked Preview (Separated Grid View)
            try:
                chunked_img = self.pixel_processor.visualize_separated_chunks(chunks, metadata)
                buffered = io.BytesIO()
                chunked_img.save(buffered, format="JPEG")
                page_previews['chunked'] = f"data:image/jpeg;base64,{base64.b64encode(buffered.getvalue()).decode('utf-8')}"
            except Exception as e:
                print(f"DEBUG: Failed to generate chunked preview: {e}")
                page_previews['chunked'] = ""

            # Shuffle chunks
            shuffled_chunks, shuffle_indices = self.pixel_processor.shuffle_chunks(
                chunks, 
                shuffle_seed + page_num  # Unique seed per page
            )
            
            # Capture Shuffled Preview - Reconstruct "unshuffled" image logic? 
            # No, visualize the shuffled state. Just unchunk directly.
            page_previews['shuffled'] = self._generate_preview(shuffled_chunks, metadata)

            # Apply DCKP-ES encryption
            encrypted_chunks = encryptor.encrypt_pixels(shuffled_chunks)
            
            # Capture Encrypted Preview
            page_previews['encrypted'] = self._generate_preview(encrypted_chunks, metadata)
            
            previews.append(page_previews)
            
            encrypted_images.append(encrypted_chunks)
            metadata_list.append(metadata)
            shuffle_indices_list.append(shuffle_indices)
        
        # Step 5-8: Package and Generate visual preview (for gallery/email)
        preview_base64 = ""
        prefix_bytes = b''
        try:
            # Reconstruct first page using encrypted chunks for the gallery image
            preview_img = self.pixel_processor.unchunk_pixels(
                encrypted_images[0], 
                metadata_list[0]
            )
            
            # Convert to bytes for PNG wrapper and base64 preview
            buffered = io.BytesIO()
            preview_img.save(buffered, format="PNG") # Use PNG for the wrapper
            prefix_bytes = buffered.getvalue()
            preview_base64 = base64.b64encode(prefix_bytes).decode('utf-8')
        except Exception as e:
            print(f"DEBUG: Failed to generate PNG prefix/preview: {e}")

        # Generate decryption key (this is what receiver needs)
        decryption_key = f"{original_filename}|{timestamp.isoformat()}"

        # Create the full package with PNG wrapper
        package_bytes = create_encryption_package(
            encrypted_images,
            metadata_list,
            shuffle_indices_list,
            prefix_bytes=prefix_bytes
        )

        # Save encrypted file with .png extension for gallery visibility
        encrypted_filename = f"encrypted_{secrets.token_hex(8)}.png"
        encrypted_dir = os.path.join(self.media_root, 'encrypted')
        os.makedirs(encrypted_dir, exist_ok=True)
        encrypted_path = os.path.join(encrypted_dir, encrypted_filename)
        
        with open(encrypted_path, 'wb') as f:
            f.write(package_bytes)
        
        # Step 6: Record transfer in database
        transfer_record = EncryptionTransfer.objects.create(
            sender_email=sender_email,
            receiver_email=receiver_email,
            original_filename=original_filename,
            encrypted_filename=encrypted_filename
        )
        
        # Step 7: Send email if requested
        email_sent = False
        print(f"DEBUG: send_email flag is {send_email}")
        if send_email:
            print("DEBUG: Calling email_service.send_encrypted_file")
            email_sent = self.email_service.send_encrypted_file(
                recipient_email=receiver_email,
                sender_email=sender_email,
                encrypted_file_path=encrypted_path,
                decryption_key=decryption_key,
                original_filename=original_filename
            )
            print(f"DEBUG: email_service returned {email_sent}")
        else:
             print("DEBUG: send_email is False, skipping email")

        return {
            'success': True,
            'transfer_id': transfer_record.id,
            'timestamp': transfer_record.timestamp.isoformat(),
            'num_pages': num_pages,
            'encrypted_file': encrypted_filename,
            'encrypted_path': encrypted_path,
            'decryption_key': decryption_key,
            'email_sent': email_sent,
            'preview_image': f"data:image/jpeg;base64,{preview_base64}" if preview_base64 else None,
            'previews': previews
        }
    
    def decrypt_pdf(
        self,
        encrypted_bytes: bytes,
        decryption_key: str
    ) -> Tuple[bytes, dict]:
        """
        Decrypt an encrypted PDF file.
        
        Args:
            encrypted_bytes: Encrypted package bytes
            decryption_key: Key in format "filename|timestamp"
            
        Returns:
            Tuple of (decrypted PDF bytes, metadata dict)
        """
        # Parse decryption key
        try:
            parts = decryption_key.split('|')
            if len(parts) != 2:
                raise ValueError("Invalid key format")
            filename, timestamp_str = parts
        except Exception as e:
            raise ValueError(f"Invalid decryption key format: {e}")
        
        # Extract encrypted package
        package = extract_encryption_package(encrypted_bytes)
        
        # Recreate encryptor from user-provided key
        # We parse the key and recreate the encryptor manually
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
            encryptor = DCKPESEncryptor(filename, timestamp)
        except Exception as e:
            raise ValueError(f"Failed to initialize decryptor from key: {e}")
        
        decrypted_images = []
        
        # Process each page
        for page_num, page_data in enumerate(package['pages']):
            encrypted_chunks = page_data['image_data']
            metadata = page_data['metadata']
            shuffle_indices = page_data['shuffle_indices']
            
            # Decrypt pixels
            decrypted_chunks = encryptor.decrypt_pixels(encrypted_chunks)
            
            # Unshuffle
            unshuffled_chunks = self.pixel_processor.unshuffle_chunks(
                decrypted_chunks,
                shuffle_indices
            )
            
            # Reconstruct image
            image = self.pixel_processor.unchunk_pixels(unshuffled_chunks, metadata)
            decrypted_images.append(image)
        
        # Reconstruct PDF
        pdf_bytes = self.pdf_processor.images_to_pdf(decrypted_images)
        
        return pdf_bytes, {
            'num_pages': len(decrypted_images),
            'original_filename': filename
        }
    
    def get_sender_history(self, sender_email: str) -> list:
        """Get transfer history for a sender."""
        return EncryptionTransfer.objects.filter(sender_email=sender_email)

    def _generate_preview(self, chunks, metadata) -> str:
        """Helper to convert chunks back to base64 image."""
        try:
            img = self.pixel_processor.unchunk_pixels(chunks, metadata)
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG")
            return f"data:image/jpeg;base64,{base64.b64encode(buffered.getvalue()).decode('utf-8')}"
        except Exception as e:
            print(f"DEBUG: Failed to generate preview: {e}")
            return ""
