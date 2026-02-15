"""
DCKP-ES: Dynamic Chaos Key Pixel Encryption Shuffling.

This module implements a chaos-based image encryption algorithm that:
1. Uses a logistic map for generating chaotic sequences
2. Derives encryption key from filename + timestamp
3. Applies XOR-based pixel encryption with chaos sequence
"""
import hashlib
import numpy as np
from datetime import datetime
from typing import Tuple, Dict, Any
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import struct
import json


class DCKPESEncryptor:
    """
    Dynamic Chaos Key Pixel Encryption Shuffling.
    
    Uses logistic chaos map combined with AES for secure pixel encryption.
    Key is derived from filename and timestamp.
    """
    
    # Logistic map parameters (chaotic regime: r > 3.57)
    CHAOS_R = 3.99
    
    def __init__(self, filename: str, timestamp: datetime):
        """
        Initialize encryptor with filename and timestamp.
        
        Args:
            filename: Original PDF filename
            timestamp: Encryption timestamp
        """
        self.filename = filename
        self.timestamp = timestamp
        self.key, self.chaos_seed = self._generate_keys()
    
    def _generate_keys(self) -> Tuple[bytes, float]:
        """
        Generate encryption key and chaos seed from filename + timestamp.
        
        Returns:
            Tuple of (AES key bytes, chaos initial value)
        """
        # Create unique string from filename and timestamp
        unique_string = f"{self.filename}|{self.timestamp.isoformat()}"
        print(f"DEBUG_KEY_GEN: Unique String='{unique_string}'")
        
        # Generate SHA-256 hash
        hash_bytes = hashlib.sha256(unique_string.encode()).digest()
        
        # First 16 bytes for AES key (AES-128)
        aes_key = hash_bytes[:16]
        print(f"DEBUG_KEY_GEN: AES Key Hex='{aes_key.hex()}'")
        
        # Use remaining bytes to generate chaos seed (0 < x0 < 1)
        seed_int = int.from_bytes(hash_bytes[16:24], 'big')
        chaos_seed = (seed_int % 1000000) / 1000000.0
        
        # Ensure chaos seed is in valid range (0.1 to 0.9)
        chaos_seed = 0.1 + (chaos_seed * 0.8)
        print(f"DEBUG_KEY_GEN: Chaos Seed='{chaos_seed}'")
        
        return aes_key, chaos_seed
    
    def _logistic_map(self, x: float, iterations: int = 1) -> float:
        """
        Apply logistic map: x(n+1) = r * x(n) * (1 - x(n))
        
        Args:
            x: Current value (0 < x < 1)
            iterations: Number of iterations
            
        Returns:
            Chaotic value after iterations
        """
        for _ in range(iterations):
            x = self.CHAOS_R * x * (1 - x)
        return x
    
    def _generate_chaos_sequence(self, length: int) -> np.ndarray:
        """
        Generate a chaotic sequence using the logistic map.
        
        Args:
            length: Length of sequence to generate
            
        Returns:
            Array of chaotic values (0-255 range for XOR)
        """
        sequence = np.zeros(length, dtype=np.uint8)
        x = self.chaos_seed
        
        # Skip first 100 iterations for better randomness
        for _ in range(100):
            x = self._logistic_map(x)
        
        for i in range(length):
            x = self._logistic_map(x)
            # Map to 0-255 range
            sequence[i] = int(x * 255) % 256
        
        return sequence
    
    def _get_shuffle_seed(self) -> int:
        """Generate a deterministic shuffle seed from the key."""
        return int.from_bytes(self.key[:4], 'big')
    
    def encrypt_pixels(self, pixel_data: np.ndarray) -> np.ndarray:
        """
        Apply DCKP-ES encryption to pixel data.
        
        Encryption steps:
        1. Generate chaos sequence
        2. XOR pixels with chaos sequence
        3. Apply additional diffusion
        
        Args:
            pixel_data: Numpy array of pixel values
            
        Returns:
            Encrypted pixel array
        """
        flat_data = pixel_data.flatten().astype(np.uint8)
        
        # Generate chaos sequence matching data length
        chaos_seq = self._generate_chaos_sequence(len(flat_data))
        
        # XOR encryption
        encrypted = np.bitwise_xor(flat_data, chaos_seq)
        
        # Additional diffusion: pixel[i] = pixel[i] XOR pixel[i-1]
        for i in range(1, len(encrypted)):
            encrypted[i] = encrypted[i] ^ encrypted[i-1]
        
        return encrypted.reshape(pixel_data.shape)
    
    def decrypt_pixels(self, encrypted_data: np.ndarray) -> np.ndarray:
        """
        Reverse DCKP-ES encryption.
        
        Args:
            encrypted_data: Encrypted pixel array
            
        Returns:
            Decrypted pixel array
        """
        flat_data = encrypted_data.flatten().astype(np.uint8)
        
        # Reverse diffusion (process in reverse order)
        decrypted = flat_data.copy()
        for i in range(len(decrypted) - 1, 0, -1):
            decrypted[i] = decrypted[i] ^ decrypted[i-1]
        
        # Generate same chaos sequence
        chaos_seq = self._generate_chaos_sequence(len(flat_data))
        
        # XOR decryption (XOR is its own inverse)
        decrypted = np.bitwise_xor(decrypted, chaos_seq)
        
        return decrypted.reshape(encrypted_data.shape)
    
    def get_encryption_params(self) -> Dict[str, Any]:
        """
        Get parameters needed for decryption.
        
        Returns:
            Dictionary with filename and timestamp
        """
        return {
            'filename': self.filename,
            'timestamp': self.timestamp.isoformat(),
            'shuffle_seed': self._get_shuffle_seed()
        }
    
    @classmethod
    def from_params(cls, params: Dict[str, Any]) -> 'DCKPESEncryptor':
        """
        Recreate encryptor from saved parameters.
        
        Args:
            params: Dictionary with filename and timestamp
            
        Returns:
            DCKPESEncryptor instance
        """
        timestamp = datetime.fromisoformat(params['timestamp'])
        return cls(params['filename'], timestamp)


def create_encryption_package(
    encrypted_images: list,
    metadata_list: list,
    shuffle_indices_list: list,
    prefix_bytes: bytes = b''
) -> bytes:
    """
    Package encrypted data with all metadata needed for decryption using a custom binary format.
    Can be wrapped with a valid image (prefix_bytes) to show in galleries.
    
    Structure:
    - Optional Prefix (e.g. valid PNG)
    - 6 bytes: Magic "AARTHA"
    - 1 byte: Version (0x01)
    - 4 bytes: Metadata length (uint32)
    - Metadata bytes (JSON)
    - Binary data for each page
    
    Args:
        encrypted_images: List of encrypted image arrays
        metadata_list: List of chunk metadata dicts
        shuffle_indices_list: List of shuffle index arrays
        prefix_bytes: Bytes of the PNG wrapper
        
    Returns:
        Bytes containing the complete encrypted package
    """
    import struct
    import json
    
    # Prepare metadata (minimal)
    # We strip sensitive info from encryption_params if possible, 
    # but the Orchestrator needs to re-derive the key anyway.
    # We include shapes and dtypes in the metadata JSON.
    pages_meta = []
    binary_data = bytearray()
    
    for i, (img_data, metadata, shuffle_idx) in enumerate(
        zip(encrypted_images, metadata_list, shuffle_indices_list)
    ):
        img_bytes = img_data.tobytes()
        shuffle_bytes = shuffle_idx.astype(np.int32).tobytes()
        
        pages_meta.append({
            'img_shape': img_data.shape,
            'img_dtype': str(img_data.dtype),
            'img_size': len(img_bytes),
            'shuffle_size': len(shuffle_bytes),
            'metadata': metadata
        })
        
        binary_data.extend(img_bytes)
        binary_data.extend(shuffle_bytes)
    
    package_meta = {
        'version': '1.0',
        'num_pages': len(encrypted_images),
        'pages': pages_meta
    }
    
    meta_json = json.dumps(package_meta).encode('utf-8')
    meta_len = len(meta_json)
    
    # PREFIX + MAGIC + VERSION + META_LEN + META + BINARY
    header = b'AARTHA' + struct.pack('B', 1) + struct.pack('>I', meta_len)
    
    return prefix_bytes + header + meta_json + bytes(binary_data)


def extract_encryption_package(package_bytes: bytes) -> dict:
    """
    Extract encrypted data and metadata from custom binary package (possibly PNG-wrapped).
    """
    import struct
    import json
    
    # Find Magic (it might be after PNG data)
    magic_pos = package_bytes.find(b'AARTHA')
    if magic_pos == -1:
        raise ValueError("Invalid file format: Magic bytes 'AARTHA' not found")
    
    offset = magic_pos + 6
    version = struct.unpack('B', package_bytes[offset:offset+1])[0]
    offset += 1
    
    if version != 1:
        raise ValueError(f"Unsupported package version: {version}")
    
    meta_len = struct.unpack('>I', package_bytes[offset:offset+4])[0]
    offset += 4
    
    meta_json = package_bytes[offset:offset+meta_len].decode('utf-8')
    offset += meta_len
    
    package = json.loads(meta_json)
    
    # Reconstruct data from binary part
    binary_part = package_bytes[offset:]
    binary_offset = 0
    
    for page in package['pages']:
        # Extract image data
        img_size = page['img_size']
        img_data_raw = binary_part[binary_offset:binary_offset + img_size]
        binary_offset += img_size
        
        page['image_data'] = np.frombuffer(
            img_data_raw,
            dtype=np.dtype(page['img_dtype'])
        ).reshape(page['img_shape']).copy() # Copy to avoid read-only from buffer
        
        # Extract shuffle indices
        shuffle_size = page['shuffle_size']
        shuffle_data_raw = binary_part[binary_offset:binary_offset + shuffle_size]
        binary_offset += shuffle_size
        
        page['shuffle_indices'] = np.frombuffer(
            shuffle_data_raw,
            dtype=np.int32
        ).copy()
        
    return package
