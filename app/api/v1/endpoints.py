from fastapi import APIRouter, UploadFile, File, HTTPException, Form
import shutil
import os
import uuid
from celery.result import AsyncResult
from app.services.tasks import process_receipt_task
from typing import List

router = APIRouter()

UPLOAD_DIR = os.getenv("UPLOAD_FOLDER", "/app/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/process-receipt")
async def process_receipt(file: UploadFile = File(...), generate_summary: bool = Form(False)):
    """
    Async Endpoint: Uploads file, pushes task to queue, returns Task ID immediately.
    """

    ALLOWED_TYPES = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
    
    if file.content_type not in ALLOWED_TYPES:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: JPG, PNG, PDF. Received: {file.content_type}"
        )
    
    # Save file to shared disk
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Trigger Celery Task( .delay() sends the message to RabbitMQ)
    task = process_receipt_task.delay(file_path, generate_summary)

    # Return the Task ID
    return {
        "task_id": task.id,
        "status": "Processing started",
        "check_status_url": f"/api/v1/tasks/{task.id}"
    }

@router.post("/process-receipt/bulk")
async def process_bulk_receipts(
    files: List[UploadFile] = File(...), 
    generate_summary: bool = Form(False)
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
            tasks.append({
                "filename": file.filename,
                "status": "error",
                "error": "Invalid file type"
            })
            continue

        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        task = process_receipt_task.delay(file_path, generate_summary)
        
        tasks.append({
            "filename": file.filename,
            "task_id": task.id,
            "status": "queued"
        })

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