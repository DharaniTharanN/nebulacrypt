import os
import django
import sys
import numpy as np
from datetime import datetime

# Setup Django configuration
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.encryption.services.pdf_processor import PDFProcessor
from apps.encryption.services.pixel_processor import PixelProcessor
from apps.encryption.services.dckp_es import DCKPESEncryptor
from apps.encryption.services.email_service import EmailService

# Minimal PDF (valid binary)
MINIMAL_PDF = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 55 >>\nstream\nBT /F1 24 Tf 50 150 Td (Test) Tj ET\nendstream\nendobj\n5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\ntrailer\n<< /Root 1 0 R /Size 6 >>\n%%EOF"

def test_full_flow():
    print("--- Starting Debug Flow ---")
    
    # 1. PDF Processing
    print("[1] Initializing PDFProcessor...")
    try:
        pdf_proc = PDFProcessor()
        print(f"    Poppler Path: {pdf_proc.poppler_path}")
        print("    Converting PDF to images...")
        images = pdf_proc.pdf_to_images(pdf_bytes=MINIMAL_PDF)
        print(f"    Success. Got {len(images)} images.")
        img = images[0]
        print(f"    Image size: {img.size}, Mode: {img.mode}")
    except Exception as e:
        print(f"!!! FAILED at PDF Processing: {e}")
        return

    # 2. Pixel Processing
    print("\n[2] Initializing PixelProcessor...")
    try:
        pix_proc = PixelProcessor()
        print("    Chunking pixels...")
        chunks, metadata = pix_proc.chunk_pixels(img)
        print(f"    Chunks shape: {chunks.shape}")
        
        print("    Shuffling chunks...")
        seed = 12345
        shuffled, indices = pix_proc.shuffle_chunks(chunks, seed)
        print("    Success.")
    except Exception as e:
        print(f"!!! FAILED at Pixel Processing: {e}")
        return

    # 3. Encryption
    print("\n[3] Initializing DCKPESEncryptor...")
    try:
        encryptor = DCKPESEncryptor("test.pdf", datetime.now())
        print("    Encrypting pixels...")
        encrypted = encryptor.encrypt_pixels(shuffled)
        print("    Success.")
    except Exception as e:
        print(f"!!! FAILED at Encryption: {e}")
        return

    # 4. Email
    print("\n[4] Testing Email Service (Mock Send)...")
    try:
        email_svc = EmailService()
        # We won't actually send unless we want to, but let's test the method call logic
        # Passing dummy paths since we didn't save files
        print("    Calling send_encrypted_file...")
        result = email_svc.send_encrypted_file(
            "test@example.com", 
            "sender@example.com", 
            "dummy_path.enc", 
            "key123", 
            "test.pdf"
        )
        print(f"    Result: {result}")
    except Exception as e:
        print(f"!!! FAILED at Email: {e}")
        return

    print("\n--- ALL SYSTEMS FUNCTIONAL ---")

if __name__ == "__main__":
    test_full_flow()
