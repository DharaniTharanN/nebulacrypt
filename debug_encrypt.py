
import os
import django
import io

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.encryption.services.encryption_orchestrator import EncryptionOrchestrator

def test_encryption():
    orch = EncryptionOrchestrator()
    # Basic PDF structure
    dummy_pdf = b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> /MediaBox [0 0 612 792] >>\nendobj\n4 0 obj\n<< /Length 20 >>\nstream\nBT /F1 24 Tf 100 700 Td (Test) Tj ET\nendstream\nendobj\n5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\ntrailer\n<< /Root 1 0 R /Size 6 >>\n%%EOF'
    
    try:
        print("Starting encryption...")
        result = orch.encrypt_pdf(
            pdf_bytes=dummy_pdf,
            original_filename='test.pdf',
            sender_email='sender@test.com',
            receiver_email='receiver@test.com',
            send_email=False
        )
        print("Encryption SUCCESS!")
        print(f"Result keys: {result.keys()}")
    except Exception as e:
        print(f"Encryption FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_encryption()
