import mimetypes
import boto3
import os
from botocore.client import Config

class StorageService:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            endpoint_url=os.getenv("S3_ENDPOINT", "http://storage:9000"),
            aws_access_key_id=os.getenv("S3_KEY", "minioadmin"),
            aws_secret_access_key=os.getenv("S3_SECRET", "minioadmin"),
            config=Config(signature_version='s3v4'),
            region_name='us-east-1'
        )
        self.bucket = "receipts"
        self._ensure_bucket()

    def _ensure_bucket(self):
        try:
            self.s3.head_bucket(Bucket=self.bucket)
        except:
            self.s3.create_bucket(Bucket=self.bucket)

    def upload_file(self, local_path, s3_key):
        content_type, _ = mimetypes.guess_type(local_path)
        content_type = content_type or 'application/octet-stream'

        self.s3.upload_file(
            local_path, 
            self.bucket, 
            s3_key,
            ExtraArgs={'ContentType': content_type}
        )
        return f"{self.bucket}/{s3_key}"

    def download_file(self, s3_key, local_path):
        self.s3.download_file(self.bucket, s3_key, local_path)

storage_service = StorageService()