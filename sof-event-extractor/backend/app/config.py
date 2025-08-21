import os
from typing import Dict, Any


def get_config() -> Dict[str, Any]:
	return {
		"AZURE_STORAGE_CONNECTION_STRING": os.getenv("AZURE_STORAGE_CONNECTION_STRING", ""),
		"AZURE_STORAGE_CONTAINER": os.getenv("AZURE_STORAGE_CONTAINER", "sof-uploads"),
		"UPLOAD_MAX_MB": int(os.getenv("UPLOAD_MAX_MB", "25")),
		"ENV": os.getenv("FLASK_ENV", "development"),
	}


