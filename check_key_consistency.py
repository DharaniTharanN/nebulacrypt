import os
import django
from datetime import datetime
import hashlib

# Setup Django configuration
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.encryption.services.dckp_es import DCKPESEncryptor

def check_key_consistency():
    print("--- Key Consistency Test ---")
    
    # 1. Simulate Encryption-side key generation
    filename = "test_file.pdf"
    ts_orig = datetime.utcnow()
    
    # Exactly what happens in encryption_orchestrator.py
    key_string = f"{filename}|{ts_orig.isoformat()}"
    print(f"Generated Key String: '{key_string}'")
    
    # 2. Derive Hash 1
    enc = DCKPESEncryptor(filename, ts_orig)
    print(f"Hash 1 (orig): {enc.key.hex()}")
    print(f"Seed 1 (orig): {enc.chaos_seed}")
    
    # 3. Simulate Decryption-side parsing
    # Using the string we generated
    try:
        parts = key_string.split('|')
        f_parsed = parts[0]
        ts_parsed_str = parts[1]
        ts_parsed = datetime.fromisoformat(ts_parsed_str)
        
        print(f"Parsed Filename: '{f_parsed}'")
        print(f"Parsed Timestamp: {ts_parsed} (iso: {ts_parsed.isoformat()})")
        
    except Exception as e:
        print(f"Parsing failed: {e}")
        return
        
    # 4. Derive Hash 2
    dec = DCKPESEncryptor(f_parsed, ts_parsed)
    print(f"Hash 2 (parsed): {dec.key.hex()}")
    print(f"Seed 2 (parsed): {dec.chaos_seed}")
    
    # Compare
    if enc.key == dec.key and enc.chaos_seed == dec.chaos_seed:
        print(">>> SUCCESS: Keys match perfectly.")
    else:
        print(">>> FAILURE: Key mismatch!")
        print(f"    Orig Key: {enc.key.hex()}")
        print(f"    Pars Key: {dec.key.hex()}")
        
    # 5. Check "String Representation" consistency
    # Does ts_orig.isoformat() == ts_parsed.isoformat()?
    if ts_orig.isoformat() == ts_parsed.isoformat():
        print("Timestamp string representation is identical.")
    else:
        print("Timestamp string representation DIFFERS!")
        print(f"    Orig: {ts_orig.isoformat()}")
        print(f"    Pars: {ts_parsed.isoformat()}")

if __name__ == "__main__":
    check_key_consistency()
