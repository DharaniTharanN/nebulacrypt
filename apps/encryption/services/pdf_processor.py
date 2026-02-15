"""
PDF Processor Service.
Converts PDF pages to images and vice versa.
"""
import os
import io
from typing import List, Tuple
from PIL import Image
from pdf2image import convert_from_path, convert_from_bytes
from django.conf import settings


class PDFProcessor:
    """Handles PDF to image conversion and reconstruction."""
    
    def __init__(self):
        self.poppler_path = getattr(settings, 'POPPLER_PATH', None)
    
    def pdf_to_images(self, pdf_path: str = None, pdf_bytes: bytes = None) -> List[Image.Image]:
        """
        Convert PDF pages to PIL Images.
        
        Args:
            pdf_path: Path to PDF file
            pdf_bytes: PDF file as bytes
            
        Returns:
            List of PIL Images, one per page
        """
        # Optimize: Reduce DPI from 150 to 100 to save memory/size
        kwargs = {'dpi': 100, 'fmt': 'PNG'}
        
        if self.poppler_path:
            kwargs['poppler_path'] = self.poppler_path
        
        if pdf_path:
            images = convert_from_path(pdf_path, **kwargs)
        elif pdf_bytes:
            images = convert_from_bytes(pdf_bytes, **kwargs)
        else:
            raise ValueError("Either pdf_path or pdf_bytes must be provided")
            
        # Optimize: Resize if too large (max 1024px width)
        optimized_images = []
        for img in images:
            if img.width > 800:
                ratio = 800 / img.width
                new_size = (800, int(img.height * ratio))
                optimized_images.append(img.resize(new_size, Image.Resampling.LANCZOS))
            else:
                optimized_images.append(img)
        
        return optimized_images
    
    def images_to_pdf(self, images: List[Image.Image]) -> bytes:
        """
        Reconstruct PDF from images.
        
        Args:
            images: List of PIL Images
            
        Returns:
            PDF file as bytes
        """
        if not images:
            raise ValueError("No images provided")
        
        pdf_buffer = io.BytesIO()
        
        # Convert all images to RGB mode if needed
        rgb_images = []
        for img in images:
            if img.mode != 'RGB':
                rgb_images.append(img.convert('RGB'))
            else:
                rgb_images.append(img)
        
        # Save as PDF
        rgb_images[0].save(
            pdf_buffer,
            'PDF',
            save_all=True,
            append_images=rgb_images[1:] if len(rgb_images) > 1 else []
        )
        
        pdf_buffer.seek(0)
        return pdf_buffer.read()
    
    def get_image_dimensions(self, image: Image.Image) -> Tuple[int, int]:
        """Get image width and height."""
        return image.size
    
    def image_to_bytes(self, image: Image.Image, format: str = 'PNG') -> bytes:
        """Convert PIL Image to bytes."""
        buffer = io.BytesIO()
        image.save(buffer, format=format)
        buffer.seek(0)
        return buffer.read()
    
    def bytes_to_image(self, image_bytes: bytes) -> Image.Image:
        """Convert bytes to PIL Image."""
        return Image.open(io.BytesIO(image_bytes))
