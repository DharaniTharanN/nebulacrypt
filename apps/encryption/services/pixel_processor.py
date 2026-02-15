"""
Pixel Processor Service.
Handles pixel chunking and shuffling operations.
"""
import numpy as np
from typing import Tuple, List
from PIL import Image
from django.conf import settings


class PixelProcessor:
    """Handles pixel chunking and shuffling for encryption."""
    
    def __init__(self, chunk_size: int = None):
        self.chunk_size = chunk_size or getattr(settings, 'CHUNK_SIZE', 32)
    
    def image_to_array(self, image: Image.Image) -> np.ndarray:
        """Convert PIL Image to numpy array."""
        return np.array(image)
    
    def array_to_image(self, array: np.ndarray) -> Image.Image:
        """Convert numpy array to PIL Image."""
        return Image.fromarray(array.astype(np.uint8))
    
    def chunk_pixels(self, image: Image.Image) -> Tuple[np.ndarray, dict]:
        """
        Break image into chunks of pixels.
        
        Each chunk is 32 pixels (flattened). The image is reshaped into
        a 1D array and then divided into chunks.
        
        Args:
            image: PIL Image to chunk
            
        Returns:
            Tuple of (chunked array, metadata dict)
        """
        # Convert to numpy array
        img_array = self.image_to_array(image)
        original_shape = img_array.shape
        
        # Flatten the array
        flat_array = img_array.flatten()
        original_size = len(flat_array)
        
        # Calculate padding needed to make divisible by chunk_size
        remainder = len(flat_array) % self.chunk_size
        if remainder != 0:
            padding = self.chunk_size - remainder
            flat_array = np.pad(flat_array, (0, padding), mode='constant', constant_values=0)
        else:
            padding = 0
        
        # Reshape into chunks
        num_chunks = len(flat_array) // self.chunk_size
        chunks = flat_array.reshape(num_chunks, self.chunk_size)
        
        metadata = {
            'original_shape': original_shape,
            'original_size': original_size,
            'padding': padding,
            'num_chunks': num_chunks,
            'chunk_size': self.chunk_size
        }
        
        return chunks, metadata
    
    def unchunk_pixels(self, chunks: np.ndarray, metadata: dict) -> Image.Image:
        """
        Reconstruct image from chunks.
        
        Args:
            chunks: Chunked pixel array
            metadata: Metadata from chunking operation
            
        Returns:
            Reconstructed PIL Image
        """
        # Flatten chunks
        flat_array = chunks.flatten()
        
        # Remove padding
        if metadata['padding'] > 0:
            flat_array = flat_array[:metadata['original_size']]
        
        # Reshape to original dimensions
        img_array = flat_array.reshape(metadata['original_shape'])
        
        return self.array_to_image(img_array)
    
    def generate_shuffle_indices(self, num_chunks: int, seed: int) -> np.ndarray:
        """
        Generate deterministic shuffle indices using a seed.
        
        Args:
            num_chunks: Number of chunks to shuffle
            seed: Random seed for reproducibility
            
        Returns:
            Array of shuffled indices
        """
        rng = np.random.RandomState(seed)
        indices = np.arange(num_chunks)
        rng.shuffle(indices)
        return indices
    
    def shuffle_chunks(self, chunks: np.ndarray, seed: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Shuffle chunks using a deterministic seed.
        
        Args:
            chunks: Array of pixel chunks
            seed: Seed for shuffle reproducibility
            
        Returns:
            Tuple of (shuffled chunks, shuffle indices for reversal)
        """
        num_chunks = len(chunks)
        shuffle_indices = self.generate_shuffle_indices(num_chunks, seed)
        
        # Apply shuffle
        shuffled_chunks = chunks[shuffle_indices]
        
        return shuffled_chunks, shuffle_indices
    
    def unshuffle_chunks(self, shuffled_chunks: np.ndarray, shuffle_indices: np.ndarray) -> np.ndarray:
        """
        Reverse the shuffle operation.
        
        Args:
            shuffled_chunks: Shuffled chunk array
            shuffle_indices: Original shuffle indices
            
        Returns:
            Unshuffled chunks in original order
        """
        # Create inverse mapping
        inverse_indices = np.argsort(shuffle_indices)
        
        # Apply inverse shuffle
        unshuffled_chunks = shuffled_chunks[inverse_indices]
        
        return unshuffled_chunks

    def visualize_separated_chunks(self, chunks: np.ndarray, metadata: dict) -> Image.Image:
        """
        Visualize chunks as separated blocks to distinguish from original image.
        
        Each 32-pixel chunk is reshaped into an 8x4 block and placed in a grid
        with padding between them.
        """
        num_chunks = len(chunks)
        chunk_size = self.chunk_size # 32
        
        # Define block dimensions for visualization (8x4 = 32 pixels)
        block_w, block_h = 8, 4
        
        # Calculate grid dimensions based on original aspect ratio approx
        orig_w, orig_h = metadata['original_shape'][1], metadata['original_shape'][0]
        ratio = orig_w / orig_h
        
        # Estimate rows/cols for blocks
        grid_cols = int(np.sqrt(num_chunks * ratio))
        grid_rows = int(np.ceil(num_chunks / grid_cols))
        
        # Padding between blocks
        pad = 2
        
        # Create output image (white background)
        out_w = (grid_cols * (block_w + pad)) + pad
        out_h = (grid_rows * (block_h + pad)) + pad
        
        # Always use Grayscale ('L') for visualization of raw data chunks
        # This avoids complexity with mapping 1D chunks to 3D RGB pixels and broadcasting errors
        out_img = Image.new('L', (out_w, out_h), color=255) 
        
        out_pixels = np.array(out_img)
        
        # Place each chunk
        for i, chunk in enumerate(chunks):
            row = i // grid_cols
            col = i % grid_cols
            
            x = pad + col * (block_w + pad)
            y = pad + row * (block_h + pad)
            
            # Reshape chunk to block
            block_data = chunk.reshape(block_h, block_w)
            
            # Place in output (Since mode is 'L', we assign values directly)
            # Clip values just in case
            out_pixels[y:y+block_h, x:x+block_w] = block_data

        return Image.fromarray(out_pixels.astype(np.uint8))

