from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends, status
import shutil
import os
import uuid
from typing import List
from fastapi.responses import StreamingResponse
import io
import mimetypes

from app.models.receipt_db import Receipt
from app.repositories.receipt import ReceiptRepository
from app.services.storage import StorageService
from app.api.dependencies import get_receipt_repository, get_storage_service
from app.services.tasks import process_receipt_task

router = APIRouter()

UPLOAD_DIR = os.getenv("UPLOAD_FOLDER", "/app/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/process-receipt", status_code=status.HTTP_201_CREATED)
async def process_receipt(
    file: UploadFile = File(...), 
    generate_summary: bool = Form(False), 
    receipt_repo: ReceiptRepository = Depends(get_receipt_repository),
    storage_service: StorageService = Depends(get_storage_service)
):
    """
    Async Endpoint: Uploads file, pushes task to queue, returns Task ID immediately.
    """
    ALLOWED_TYPES = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
    
    if file.content_type not in ALLOWED_TYPES:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: JPG, PNG, PDF. Received: {file.content_type}"
        )
    
    temp_id = str(uuid.uuid4())
    unique_filename = f"{temp_id}_{file.filename}"
    local_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    try:
        with open(local_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Upload to MinIO
        s3_key = f"uploads/{unique_filename}"
        storage_service.upload_file(local_path, s3_key)
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)

    # Trigger Task
    task = process_receipt_task.delay(s3_key, generate_summary)

    # Create DB Record
    db_receipt = Receipt(
        task_id=task.id,
        filename=file.filename,
        s3_key=s3_key,
        status="pending"
    )
    await receipt_repo.create(db_receipt)

    return {"task_id": task.id, "status": "Processing"}

@router.post("/process-receipt/bulk", status_code=status.HTTP_201_CREATED)
async def process_bulk_receipts(
    files: List[UploadFile] = File(...), 
    generate_summary: bool = Form(False),
    receipt_repo: ReceiptRepository = Depends(get_receipt_repository),
    storage_service: StorageService = Depends(get_storage_service)
):
    """
    Accepts multiple files, creates a task for each, returns a list of Task IDs.
    """
    if len(files) > 20:
        raise HTTPException(status_code=400, detail="Max 20 files allowed per batch.")

    tasks = []

    for file in files:
        if file.content_type not in ["image/jpeg", "image/png", "image/jpg", "application/pdf"]:
            tasks.append({"filename": file.filename, "status": "error", "error": "Invalid file type"})
            continue

        temp_id = str(uuid.uuid4())
        unique_filename = f"{temp_id}_{file.filename}"
        local_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        try:
            with open(local_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            s3_key = f"uploads/{unique_filename}"
            storage_service.upload_file(local_path, s3_key)

            task = process_receipt_task.delay(s3_key, generate_summary)
            
            db_receipt = Receipt(
                task_id=task.id,
                filename=file.filename,
                s3_key=s3_key,
                status="pending"
            )
            await receipt_repo.create(db_receipt)
            
            tasks.append({
                "filename": file.filename,
                "task_id": task.id,
                "status": "queued"
            })
        finally:
            if os.path.exists(local_path):
                os.remove(local_path)

    return {"batch_id": str(uuid.uuid4()), "tasks": tasks}

@router.get("/receipts/history")
async def get_history(receipt_repo: ReceiptRepository = Depends(get_receipt_repository)):
    return await receipt_repo.get_history()

@router.get("/receipts/{receipt_id}/file")
async def get_receipt_file(
    receipt_id: int, 
    receipt_repo: ReceiptRepository = Depends(get_receipt_repository),
    storage_service: StorageService = Depends(get_storage_service)
):
    receipt = await receipt_repo.get(receipt_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")

    try:
        response = storage_service.get_object(receipt.s3_key)
        
        content_type = response.get('ContentType')
        if not content_type or content_type == 'application/octet-stream':
            content_type, _ = mimetypes.guess_type(receipt.filename)
            content_type = content_type or 'application/octet-stream'

        headers = {
            "Content-Disposition": f'inline; filename="{receipt.filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
        
        return StreamingResponse(
            io.BytesIO(response['Body'].read()), 
            media_type=content_type,
            headers=headers
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not retrieve file: {str(e)}")
