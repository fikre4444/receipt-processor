import os
import boto3
from botocore.client import Config
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session
from app.repositories.receipt import ReceiptRepository
from app.services.storage import StorageService
from app.services.ocr import OCRService
from app.services.llm import LLMService
from app.services.image import ImageService
from app.services.analysis import AnalysisService

# Storage Client
def get_s3_client():
    return boto3.client(
        's3',
        endpoint_url=os.getenv("S3_ENDPOINT", "http://storage:9000"),
        aws_access_key_id=os.getenv("S3_KEY", "minioadmin"),
        aws_secret_access_key=os.getenv("S3_SECRET", "minioadmin"),
        config=Config(signature_version='s3v4'),
        region_name='us-east-1'
    )

# Service Providers
def get_storage_service(s3_client=Depends(get_s3_client)) -> StorageService:
    return StorageService(s3_client)

def get_ocr_service() -> OCRService:
    return OCRService()

def get_llm_service() -> LLMService:
    return LLMService()

def get_image_service() -> ImageService:
    return ImageService()

def get_analysis_service() -> AnalysisService:
    return AnalysisService()

# Repository Providers
def get_receipt_repository(session: AsyncSession = Depends(get_async_session)) -> ReceiptRepository:
    return ReceiptRepository(session)
