import os
import json
import requests


def main() -> None:
	pplx_key = os.getenv("PPLX_API_KEY", "").strip()
	if not pplx_key:
		print("PPLX_API_KEY not set")
		return

	url = "https://api.perplexity.ai/chat/completions"
	headers = {"Authorization": f"Bearer {pplx_key}", "Content-Type": "application/json"}
	payload = {
		"model": os.getenv("PPLX_MODEL", "llama-3.1-sonar-small-128k"),
		"temperature": 0.0,
		"messages": [
			{"role": "system", "content": "Return ONLY JSON {\"events\":[{\"name\":str,\"start\":str,\"end\":str}]}"},
			{"role": "user", "content": "Loading 10:00 - 12:00\nBerthing 01/07/2025 08:30-09:10"},
		],
	}

	try:
		resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
		print("status:", resp.status_code, "ok:", resp.ok)
		print("preview:", (resp.text or "")[:500].replace("\n", " "))
	except Exception as exc:
		print("error:", str(exc))


if __name__ == "__main__":
	main()


