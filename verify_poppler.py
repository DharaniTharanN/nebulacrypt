# verify_poppler.py
"""Simple script to verify Poppler installation and PDF page count.
It loads POPPLER_PATH from the Django settings (if available) or the
environment variable, then uses pdf2image to convert a minimal PDF and
prints the number of pages.
"""
import os
import sys
from pdf2image import convert_from_bytes

# Minimal one‑page PDF (binary data)
MINIMAL_PDF = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 55 >>\nstream\nBT /F1 24 Tf 50 150 Td (Test) Tj ET\nendstream\nendobj\n5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\ntrailer\n<< /Root 1 0 R /Size 6 >>\n%%EOF"

# Get POPPLER_PATH from settings
try:
    import os
    import django
    from django.conf import settings
    
    # Setup Django standalone
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    if not settings.configured:
        django.setup()
        
    poppler_path = getattr(settings, 'POPPLER_PATH', None)
    print(f"Using POPPLER_PATH: '{poppler_path}'")
except Exception as e:
    print(f"Failed to load settings: {e}")
    poppler_path = None

kwargs = {'dpi': 150, 'fmt': 'PNG'}
if poppler_path:
    kwargs['poppler_path'] = poppler_path

try:
    images = convert_from_bytes(MINIMAL_PDF, **kwargs)
    print(f"Poppler is working. Page count: {len(images)}")
except Exception as e:
    print("Error using Poppler:")
    print(e)
    sys.exit(1)
