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

	# Parse events (stub implementation for now)
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


