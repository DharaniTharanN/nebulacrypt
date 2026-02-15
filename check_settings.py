import os
import django
from django.conf import settings

# Setup Django standalone
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

print(f"POPPLER_PATH from settings: '{settings.POPPLER_PATH}'")
print(f"POPPLER_PATH from os.environ: '{os.environ.get('POPPLER_PATH')}'")

# Try to verify the path if it exists
if settings.POPPLER_PATH:
    if os.path.exists(settings.POPPLER_PATH):
        print(f"Path exists: Yes")
        print(f"Directory contents: {os.listdir(settings.POPPLER_PATH)}")
    else:
        print(f"Path exists: No")
else:
    print("POPPLER_PATH is not set in settings.")
