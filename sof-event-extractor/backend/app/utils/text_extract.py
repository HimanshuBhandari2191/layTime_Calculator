from __future__ import annotations

import io
from typing import Optional

from docx import Document
from app.services.ocr_service import OCRService


def bytes_to_text(file_bytes: bytes, filename: str) -> str:
    """Extract text from various file formats using OCR and document parsers.
    
    Supports:
    - .txt: Direct text extraction
    - .pdf: OCR using Tesseract
    - .docx: python-docx extraction
    - .jpg, .png, .tiff: OCR using Tesseract
    """
    name = filename.lower()
    
    # Text files
    if name.endswith(".txt"):
        try:
            return file_bytes.decode("utf-8", errors="replace")
        except Exception:
            return ""
    
    # PDF files - use OCR
    elif name.endswith(".pdf"):
        ocr_service = OCRService()
        return ocr_service.extract_text_from_pdf(file_bytes)
    
    # Word documents - use python-docx
    elif name.endswith((".docx", ".doc")):
        try:
            doc = Document(io.BytesIO(file_bytes))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            print(f"DOCX extraction failed: {e}")
            return ""
    
    # Image files - use OCR
    elif name.endswith((".jpg", ".jpeg", ".png", ".tiff", ".bmp")):
        ocr_service = OCRService()
        return ocr_service.extract_text_from_image(file_bytes)
    
    # Unknown format
    else:
        print(f"Unsupported file format: {filename}")
        return ""


