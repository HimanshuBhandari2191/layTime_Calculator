from __future__ import annotations

import io
import os
from typing import List, Optional

import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image, ImageEnhance, ImageFilter


class OCRService:
    """Tesseract OCR service for extracting text from PDFs and images."""

    def __init__(self) -> None:
        # Configure Tesseract path if needed (Windows)
        if os.name == 'nt':  # Windows
            # Common Tesseract installation paths on Windows
            possible_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Users\Himanshu Bhandari\AppData\Local\Programs\Tesseract-OCR\tesseract.exe',
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    break

    def extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        """Convert PDF to images and extract text using Tesseract OCR."""
        try:
            # Convert PDF pages to images
            images = convert_from_bytes(pdf_bytes, dpi=300)
            
            extracted_text = ""
            for i, image in enumerate(images):
                # Preprocess image for better OCR
                processed_image = self._preprocess_image(image)
                
                # Extract text from the processed image
                page_text = pytesseract.image_to_string(
                    processed_image, 
                    config='--psm 6'  # Assume uniform block of text
                )
                extracted_text += f"\n--- Page {i+1} ---\n{page_text}\n"
            
            return extracted_text.strip()
        except Exception as e:
            print(f"OCR extraction failed: {e}")
            return ""

    def extract_text_from_image(self, image_bytes: bytes) -> str:
        """Extract text from image bytes using Tesseract OCR."""
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Preprocess image
            processed_image = self._preprocess_image(image)
            
            # Extract text
            text = pytesseract.image_to_string(
                processed_image, 
                config='--psm 6'
            )
            return text.strip()
        except Exception as e:
            print(f"Image OCR extraction failed: {e}")
            return ""

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR accuracy."""
        # Convert to grayscale
        if image.mode != 'L':
            image = image.convert('L')
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # Apply slight blur to reduce noise
        image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.5)
        
        return image
