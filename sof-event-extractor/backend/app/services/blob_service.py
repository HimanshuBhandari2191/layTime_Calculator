from datetime import datetime
from azure.storage.blob import BlobServiceClient


class BlobUploader:
	def __init__(self, connection_string: str, container_name: str) -> None:
		self._client = BlobServiceClient.from_connection_string(connection_string)
		self._container = container_name
		self._ensure_container_exists()

	def _ensure_container_exists(self) -> None:
		container = self._client.get_container_client(self._container)
		if not container.exists():
			container.create_container()

	def upload_bytes(self, data: bytes, filename: str) -> str:
		stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S%fZ")
		blob_name = f"uploads/{stamp}-{filename}"
		blob_client = self._client.get_blob_client(container=self._container, blob=blob_name)
		blob_client.upload_blob(data, overwrite=True)
		return blob_name


