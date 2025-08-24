import pytesseract
from PIL import Image
import fitz  # PyMuPDF for PDFs

def extract_text(file_path):
    text = ""
    if file_path.lower().endswith(".pdf"):
        doc = fitz.open(file_path)
        for page in doc:
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            text += pytesseract.image_to_string(img)
    else:
        text = pytesseract.image_to_string(Image.open(file_path))
    return text
