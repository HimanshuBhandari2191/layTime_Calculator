from flask import Blueprint, request, jsonify, send_file
import io
import csv

from .config import get_config
from .db import get_sql_connection
from .services.blob_service import BlobUploader
from .parsers.sof_parser import extract_events


api_bp = Blueprint("api", __name__)


def _get_uploader() -> BlobUploader | None:
	cfg = get_config()
	connection_string = cfg.get("AZURE_STORAGE_CONNECTION_STRING")
	container = cfg.get("AZURE_STORAGE_CONTAINER")
	if not connection_string or not container:
		return None
	return BlobUploader(connection_string, container)


@api_bp.post("/upload")
def upload():
	if "file" not in request.files:
		return {"error": "Missing file form field 'file'"}, 400

	uploaded_file = request.files["file"]
	file_bytes = uploaded_file.read()

	# Parse events using OCR + NLP pipeline
	parsed = extract_events(file_bytes, uploaded_file.filename)

	# Upload original document to Azure Blob if configured
	uploader = _get_uploader()
	blob_name = None
	if uploader is not None:
		try:
			blob_name = uploader.upload_bytes(file_bytes, uploaded_file.filename)
		except Exception as exc:
			# Continue even if upload fails; surface message
			return jsonify({"result": parsed, "blob": None, "upload_error": str(exc)}), 200

	return jsonify({"result": parsed, "blob": blob_name}), 200


@api_bp.get("/test-ocr")
def test_ocr():
	"""Test endpoint to verify OCR functionality."""
	from app.services.ocr_service import OCRService
	
	# Create a simple test image with text
	from PIL import Image, ImageDraw, ImageFont
	import io
	
	# Create a test image
	img = Image.new('RGB', (400, 200), color='white')
	draw = ImageDraw.Draw(img)
	
	# Add some maritime text
	test_text = "Cargo Loading\nStart: 08:30\nEnd: 14:45"
	draw.text((20, 20), test_text, fill='black')
	
	# Convert to bytes
	img_bytes = io.BytesIO()
	img.save(img_bytes, format='PNG')
	img_bytes.seek(0)
	
	# Test OCR
	ocr_service = OCRService()
	extracted_text = ocr_service.extract_text_from_image(img_bytes.getvalue())
	
	return jsonify({
		"ocr_working": bool(extracted_text),
		"extracted_text": extracted_text,
		"test_image_created": True
	}), 200


@api_bp.post("/export/json")
def export_json():
	payload = request.get_json(silent=True) or {}
	return jsonify(payload), 200


@api_bp.post("/export/csv")
def export_csv():
	payload = request.get_json(silent=True) or {}
	events = payload.get("events", [])
	output = io.StringIO()
	writer = csv.DictWriter(output, fieldnames=["name", "start", "end"])
	writer.writeheader()
	for e in events:
		writer.writerow({
			"name": e.get("name", ""),
			"start": e.get("start", ""),
			"end": e.get("end", ""),
		})
	mem = io.BytesIO(output.getvalue().encode("utf-8"))
	mem.seek(0)
	return send_file(mem, mimetype="text/csv", as_attachment=True, download_name="events.csv")


@api_bp.get("/db/version")
def db_version():
	try:
		with get_sql_connection() as conn:
			cursor = conn.cursor()
			cursor.execute("SELECT @@VERSION;")
			row = cursor.fetchone()
			return jsonify({"version": row[0] if row else None}), 200
	except Exception as exc:
		return jsonify({"error": str(exc)}), 500


