import os
import django
import sys

# Setup Django standalone
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

try:
    from apps.encryption.services.pdf_processor import PDFProcessor
    
    print("Instantiating PDFProcessor...")
    processor = PDFProcessor()
    
    print(f"Processor initialized.")
    print(f"Poppler Path in processor: '{processor.poppler_path}'")
    
    if processor.poppler_path:
        print("Poppler path is set in the processor.")
        if os.path.exists(processor.poppler_path):
             print("Path exists on disk.")
        else:
             print("WARNING: Path does NOT exist on disk.")
    else:
        print("ERROR: Poppler path is None in the processor!")

except ImportError as e:
    print(f"ImportError: {e}")
    # Adjust path if needed (though django.setup should handle it if run from root)
except Exception as e:
    print(f"An error occurred: {e}")
