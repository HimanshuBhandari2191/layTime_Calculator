from flask import Flask, request, jsonify
from flask_cors import CORS
import pytesseract
from PIL import Image
import fitz  # PyMuPDF for PDFs
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
def create_app():
    app = Flask(__name__)
    CORS(app)
	
    @app.route("/api/upload", methods=["POST"])
    def upload_file():
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        text = ""
        if file.filename.lower().endswith(".pdf"):
            # Read PDF pages and OCR them
            pdf_bytes = file.read()
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            for page in doc:
                pix = page.get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                text += pytesseract.image_to_string(img) + "\n"
        else:
            # OCR image files
            image = Image.open(file.stream)
            text = pytesseract.image_to_string(image)

        return jsonify({
            "message": "Upload successful",
            "filename": file.filename,
            "text": text[:2000]  # return first 2000 chars
        }), 200

    return app
