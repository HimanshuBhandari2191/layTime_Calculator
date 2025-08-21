from __future__ import annotations

from typing import Optional


def bytes_to_text(file_bytes: bytes, filename: str) -> str:
	"""Very simple extractor stub. Extend with PDF/DOCX libraries if needed.

	For now, if the file appears textual, decode as utf-8 with replacement.
	Otherwise, return an empty string and rely on future OCR integration.
	"""
	name = filename.lower()
	if name.endswith(".txt"):
		try:
			return file_bytes.decode("utf-8", errors="replace")
		except Exception:
			return ""
	# TODO: integrate pdfminer.six / pymupdf for PDFs and python-docx for DOCX
	return ""


