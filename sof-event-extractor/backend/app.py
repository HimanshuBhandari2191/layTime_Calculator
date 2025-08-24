import os
import io
import re
import csv
import json
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract
import fitz  # PyMuPDF for PDFs

# ✅ Initialize Flask
app = Flask(__name__)
CORS(app)

# ✅ Path to Tesseract OCR (update if needed)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# --- Parser function (make structured output) ---
def parse_ocr_text(text):
    events = []
    cargo = []
    remarks = ""
    total_cargo = 0

    lines = text.splitlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # --- Event detection (basic time + date pattern) ---
        match = re.match(r"(.+?)\s+(\d{3,4})\s+HOURS\s+(\d{2}\.\d{2}\.\d{4})", line, re.IGNORECASE)
        if match:
            event_name = match.group(1).title()
            start_time = match.group(2)[:2] + ":" + match.group(2)[2:]
            events.append({
                "event": event_name,
                "start_time": start_time,
                "end_time": None,
                "date": match.group(3)
            })
            continue

        # --- Cargo detection (find trailing numbers) ---
        if any(x in line.upper() for x in ["CARGO", "STEAM", "BULK"]):
            parts = line.rsplit(" ", 1)
            if len(parts) == 2 and parts[1].replace(",", "").isdigit():
                cargo.append({
                    "description": parts[0].title(),
                    "tonnage": int(parts[1].replace(",", ""))
                })
            continue

        # --- Remarks detection ---
        if "REMARKS" in line.upper():
            remarks = line
            continue

    # ✅ Avoid double-counting "Total Cargo"
    total_cargo = sum(item["tonnage"] for item in cargo if "total" not in item["description"].lower())

    return {
        "events": events,
        "cargo": cargo,
        "remarks": remarks,
        "total_cargo": total_cargo
    }


# --- Route: Upload File ---
@app.route("/api/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    filename = secure_filename(file.filename)
    text = ""

    try:
        if filename.lower().endswith(".pdf"):
            # ✅ Process PDF with PyMuPDF
            pdf_bytes = file.read()
            pdf = fitz.open(stream=pdf_bytes, filetype="pdf")

            for page_num in range(len(pdf)):
                page = pdf.load_page(page_num)
                pix = page.get_pixmap()
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                text += pytesseract.image_to_string(img) + "\n"

        else:
            # ✅ Process Image (JPG, PNG, etc.)
            img = Image.open(io.BytesIO(file.read()))
            text = pytesseract.image_to_string(img)

        # ✅ Parse OCR into structured JSON
        structured = parse_ocr_text(text)

        return jsonify({
            "message": "Upload successful",
            "filename": filename,
            "data": structured
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Route: Export JSON ---
@app.route("/api/export/json", methods=["POST"])
def export_json():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        response = Response(json.dumps(data, indent=2), mimetype="application/json")
        response.headers["Content-Disposition"] = "attachment; filename=sof_export.json"
        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Route: Export CSV ---
@app.route("/api/export/csv", methods=["POST"])
def export_csv():
    try:
        data = request.json  # frontend sends parsed JSON here
        if not data or "data" not in data:
            return jsonify({"error": "No data provided"}), 400

        output = io.StringIO()
        writer = csv.writer(output)

        # --- Write EVENTS ---
        writer.writerow(["Section", "Event", "Start Time", "End Time", "Date"])
        for ev in data["data"].get("events", []):
            writer.writerow(["Event", ev.get("event"), ev.get("start_time"), ev.get("end_time"), ev.get("date")])

        # --- Write CARGO ---
        writer.writerow([])
        writer.writerow(["Section", "Description", "Tonnage"])
        for cg in data["data"].get("cargo", []):
            writer.writerow(["Cargo", cg.get("description"), cg.get("tonnage")])

        # --- Write REMARKS ---
        writer.writerow([])
        writer.writerow(["Section", "Remarks"])
        writer.writerow(["Remarks", data["data"].get("remarks", "")])

        # --- Write Total Cargo ---
        writer.writerow([])
        writer.writerow(["Section", "Total Cargo"])
        writer.writerow(["Cargo Summary", data["data"].get("total_cargo", 0)])

        response = Response(output.getvalue(), mimetype="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=sof_export.csv"
        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Main entry point ---
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
