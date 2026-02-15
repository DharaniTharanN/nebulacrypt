import os
import numpy as np
import django
from datetime import datetime
from PIL import Image

# Setup Django configuration
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.encryption.services.pixel_processor import PixelProcessor
from apps.encryption.services.dckp_es import DCKPESEncryptor

def test_algo_reproduction():
    print("--- Algorithm Reproduction Test ---")
    
    # 1. Create a dummy gradient image (100x100)
    width, height = 100, 100
    arr = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            arr[y, x] = [x % 255, y % 255, (x+y) % 255]
    
    original_img = Image.fromarray(arr)
    print(f"[1] Created dummy image: {original_img.size}")
    
    # 2. Key Params
    filename = "test_image.jpg"
    timestamp = datetime.utcnow()
    print(f"[2] Key Params: Filename={filename}, Timestamp={timestamp.isoformat()}")
    
    # --- ENCRYPTION PHASE ---
    
    # A. Chunking
    pp = PixelProcessor(chunk_size=32)
    chunks, metadata = pp.chunk_pixels(original_img)
    print(f"[3] Chunked: {chunks.shape} chunks")
    
    # B. Encryption Setup
    encryptor = DCKPESEncryptor(filename, timestamp)
    print(f"    Chaos Seed: {encryptor.chaos_seed}")
    shuffle_seed = encryptor._get_shuffle_seed()
    print(f"    Shuffle Seed: {shuffle_seed}")
    
    # C. Shuffling
    shuffled_chunks, shuffle_indices = pp.shuffle_chunks(chunks, shuffle_seed)
    
    # D. Encrypting Pixels
    encrypted_chunks = encryptor.encrypt_pixels(shuffled_chunks)
    print("[4] Encryption complete")
    
    # --- DECRYPTION PHASE ---
    
    # E. Decryption Setup (Recreate Encryptor from same params)
    decryptor = DCKPESEncryptor(filename, timestamp)
    print(f"[5] Decryptor initialized. Seed match? {encryptor.chaos_seed == decryptor.chaos_seed}")
    
    # F. Decrypt Pixels
    decrypted_shuffled_chunks = decryptor.decrypt_pixels(encrypted_chunks)
    
    # Verify Step F vs Step C (Should be identical)
    diff_encrypted = np.array_equal(shuffled_chunks, decrypted_shuffled_chunks)
    print(f"    Decrypted Pixels Match Shuffled Chunks? {diff_encrypted}")
    if not diff_encrypted:
        print("    !!! XOR REVERSAL FAILED !!!")
        # Sample check
        print(f"    Orig[0]: {shuffled_chunks[0][:5]}")
        print(f"    Decr[0]: {decrypted_shuffled_chunks[0][:5]}")
    
    # G. Unshuffling
    unshuffled_chunks = pp.unshuffle_chunks(decrypted_shuffled_chunks, shuffle_indices)
    
    # Verify Step G vs Step A
    diff_chunks = np.array_equal(chunks, unshuffled_chunks)
    print(f"    Unshuffled Chunks Match Original? {diff_chunks}")
    
    # H. Reconstruction
    reconstructed_img = pp.unchunk_pixels(unshuffled_chunks, metadata)
    
    # Final Pixel Compare
    recon_arr = np.array(reconstructed_img)
    orig_arr = np.array(original_img)
    is_identical = np.array_equal(orig_arr, recon_arr)
    
    print(f"[6] Final Image Identical? {is_identical}")
    
    if is_identical:
        print(">>> SUCCESS: Algorithm is reversible.")
    else:
        print(">>> FAILURE: Algorithm is NOT reversible.")

if __name__ == "__main__":
    test_algo_reproduction()
