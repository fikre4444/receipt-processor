from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends, status
import shutil
import os
import uuid
from celery.result import AsyncResult
from typing import List
from sqlmodel import Session, select
from fastapi.responses import StreamingResponse
import io
from app.services.tasks import process_receipt_task
from app.models.receipt_db import Receipt
from app.db import get_session
from app.services.storage_service import storage_service
import mimetypes

router = APIRouter()

UPLOAD_DIR = os.getenv("UPLOAD_FOLDER", "/app/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/process-receipt")
async def process_receipt(file: UploadFile = File(...), generate_summary: bool = Form(False), session: Session = Depends(get_session)):
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
    
    with open(local_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Upload to MinIO
    s3_key = f"uploads/{unique_filename}"
    storage_service.upload_file(local_path, s3_key)
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
    session.add(db_receipt)
    session.commit()

    return {"task_id": task.id, "status": "Processing"}


@router.post("/process-receipt/bulk")
async def process_bulk_receipts(
    files: List[UploadFile] = File(...), 
    generate_summary: bool = Form(False),
    session: Session = Depends(get_session)
):
    """
    Accepts multiple files, creates a task for each, returns a list of Task IDs.
    """
    
    if len(files) > 20:
        raise HTTPException(status_code=400, detail="Max 20 files allowed per batch.")

    tasks = []

    for file in files:
        # Validate type
        if file.content_type not in ["image/jpeg", "image/png", "image/jpg", "application/pdf"]:
            tasks.append({"filename": file.filename, "status": "error", "error": "Invalid file type"})
            continue

        temp_id = str(uuid.uuid4())
        unique_filename = f"{temp_id}_{file.filename}"
        local_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        with open(local_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        s3_key = f"uploads/{unique_filename}"
        storage_service.upload_file(local_path, s3_key)

        task = process_receipt_task.delay(s3_key, generate_summary)
        
        if os.path.exists(local_path):
            os.remove(local_path)

        db_receipt = Receipt(
            task_id=task.id,
            filename=file.filename,
            s3_key=s3_key,
            status="pending"
        )
        session.add(db_receipt)
        
        tasks.append({
            "filename": file.filename,
            "task_id": task.id,
            "status": "queued"
        })

    session.commit()
    return {"batch_id": str(uuid.uuid4()), "tasks": tasks}

@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """
    Poll this endpoint to get the result.
    """
    task_result = AsyncResult(task_id)
    
    if task_result.state == 'PENDING':
        return {"state": "PENDING", "status": "Task is waiting in queue..."}
    
    elif task_result.state == 'STARTED':
        return {"state": "STARTED", "status": "Task is currently processing..."}
    
    elif task_result.state == 'SUCCESS':
        return {"state": "SUCCESS", "result": task_result.result}
    
    elif task_result.state == 'FAILURE':
        return {"state": "FAILURE", "error": str(task_result.info)}
    
    return {"state": task_result.state}

@router.get("/receipts/history")
async def get_history(session: Session = Depends(get_session)):
    return session.exec(select(Receipt).order_by(Receipt.created_at.desc())).all()


@router.get("/receipts/{receipt_id}/file")
async def get_receipt_file(receipt_id: int, session: Session = Depends(get_session)):
    receipt = session.get(Receipt, receipt_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")

    try:
        response = storage_service.s3.get_object(
            Bucket=storage_service.bucket, 
            Key=receipt.s3_key
        )
        
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