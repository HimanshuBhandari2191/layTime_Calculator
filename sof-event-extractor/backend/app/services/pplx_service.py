from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import requests


class PerplexityClient:
	"""Minimal client for Perplexity's Chat Completions API.

	Set environment variables:
	- PPLX_API_KEY
	- PPLX_MODEL (optional)
	"""

	API_URL = "https://api.perplexity.ai/chat/completions"

	def __init__(self) -> None:
		self._api_key = os.getenv("PPLX_API_KEY", "").strip()
		self._model = os.getenv("PPLX_MODEL", "llama-3.1-sonar-small-128k").strip()

	def is_configured(self) -> bool:
		return bool(self._api_key)

	def extract_events(self, text: str) -> Optional[List[Dict[str, Any]]]:
		"""Ask the model to extract events with start/end times. Returns list or None on error."""
		if not self.is_configured():
			return None

		headers = {
			"Authorization": f"Bearer {self._api_key}",
			"Content-Type": "application/json",
		}
		prompt = (
			"You are an extraction engine. From the provided Statement of Facts text, "
			"detect event entries (e.g., loading, berthing, anchorage, shifting, cargo operations) and "
			"their start and end times. Return ONLY JSON with an 'events' array of objects: "
			"[{\"name\": str, \"start\": str or null, \"end\": str or null}]. "
			"Times should be ISO 8601 if possible; otherwise copy as-is. Do not include explanations."
		)
		payload = {
			"model": self._model,
			"temperature": 0.0,
			"messages": [
				{"role": "system", "content": prompt},
				{"role": "user", "content": text},
			],
		}
		try:
			resp = requests.post(self.API_URL, headers=headers, data=json.dumps(payload), timeout=60)
			resp.raise_for_status()
			data = resp.json()
			content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
			# content should be JSON per our instruction
			parsed = json.loads(content)
			return parsed.get("events") if isinstance(parsed, dict) else parsed
		except Exception:
			return None


