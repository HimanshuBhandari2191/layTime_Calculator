from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
from nlp_service.ocr import extract_text  # <-- you’ll create this inside nlp-service

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files["file"]
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # Run OCR/NLP
    extracted_text = extract_text(filepath)

    return jsonify({"filename": filename, "text": extracted_text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
