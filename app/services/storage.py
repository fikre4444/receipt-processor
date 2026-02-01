import mimetypes
from typing import Any
import boto3
from botocore.client import Config

class StorageService:
    def __init__(self, s3_client: Any, bucket_name: str = "receipts"):
        self.s3 = s3_client
        self.bucket = bucket_name
        self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        try:
            self.s3.head_bucket(Bucket=self.bucket)
        except Exception:
            try:
                self.s3.create_bucket(Bucket=self.bucket)
            except Exception:
                # In some cases (like localstack or specific MinIO configs), 
                # bucket creation might fail if already exists or due to permissions
                pass

    def upload_file(self, local_path: str, s3_key: str) -> str:
        content_type, _ = mimetypes.guess_type(local_path)
        content_type = content_type or 'application/octet-stream'

        self.s3.upload_file(
            local_path, 
            self.bucket, 
            s3_key,
            ExtraArgs={'ContentType': content_type}
        )
        return f"{self.bucket}/{s3_key}"

    def download_file(self, s3_key: str, local_path: str) -> None:
        self.s3.download_file(self.bucket, s3_key, local_path)

    def get_object(self, s3_key: str) -> Any:
        return self.s3.get_object(Bucket=self.bucket, Key=s3_key)
