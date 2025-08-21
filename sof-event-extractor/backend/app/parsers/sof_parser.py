from __future__ import annotations

from typing import Dict, Any, List
import os
import re

from app.services.pplx_service import PerplexityClient
from app.utils.text_extract import bytes_to_text


def extract_events(file_bytes: bytes, filename: str) -> Dict[str, Any]:
	text = bytes_to_text(file_bytes, filename)

	# 1) Perplexity LLM if configured
	pplx = PerplexityClient()
	if pplx.is_configured() and text:
		events = pplx.extract_events(text)
		if events:
			return {"filename": filename, "events": events}

	# 2) Regex fallback
	events = _regex_extract(text) if text else _demo_events()
	return {"filename": filename, "events": events}


def _demo_events() -> List[Dict[str, str]]:
	return [
		{"name": "Vessel Arrived", "start": "2025-07-01T08:00:00Z", "end": "2025-07-01T08:15:00Z"},
		{"name": "Pilot Onboard", "start": "2025-07-01T08:30:00Z", "end": "2025-07-01T08:45:00Z"},
		{"name": "Berthing", "start": "2025-07-01T09:00:00Z", "end": "2025-07-01T09:30:00Z"},
	]


KEYWORDS = [
	"loading",
	"berthing",
	"anchorage",
	"shifting",
	"unloading",
]

TIME_PATTERN = re.compile(
	# Matches various forms like 08:30, 8:30, 01/07/2025 08:30, 2025-07-01 08:30, etc.
	r"((\d{1,2}:\d{2})|((\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+\d{1,2}:\d{2})|(\d{4}-\d{2}-\d{2}\s+\d{1,2}:\d{2}))",
	re.IGNORECASE,
)


def _regex_extract(text: str) -> List[Dict[str, str]]:
	lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
	results: List[Dict[str, str]] = []
	for ln in lines:
		low = ln.lower()
		if any(k in low for k in KEYWORDS):
			matches = TIME_PATTERN.findall(ln)
			# Flatten matches and pick up to two time-like tokens
			times: List[str] = []
			for m in matches:
				candidate = m[0] if isinstance(m, tuple) else m
				if candidate:
					times.append(candidate)
				if len(times) >= 2:
					break
			results.append({
				"name": ln,
				"start": times[0] if len(times) >= 1 else "",
				"end": times[1] if len(times) >= 2 else "",
			})
	return results


