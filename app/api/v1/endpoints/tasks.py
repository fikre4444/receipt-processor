from fastapi import APIRouter
from celery.result import AsyncResult
from app.core.celery_app import celery_app

router = APIRouter()

@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """
    Poll this endpoint to get the result.
    """
    task_result = AsyncResult(task_id, app=celery_app)
    
    if task_result.state == 'PENDING':
        return {"state": "PENDING", "status": "Task is waiting in queue..."}
    
    elif task_result.state == 'STARTED':
        return {"state": "STARTED", "status": "Task is currently processing..."}
    
    elif task_result.state == 'SUCCESS':
        return {"state": "SUCCESS", "result": task_result.result}
    
    elif task_result.state == 'FAILURE':
        return {"state": "FAILURE", "error": str(task_result.info)}
    
    return {"state": task_result.state}
