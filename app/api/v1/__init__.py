from fastapi import APIRouter
from app.api.v1.endpoints import receipts, tasks

router = APIRouter()
router.include_router(receipts.router, tags=["receipts"])
router.include_router(tasks.router, tags=["tasks"])
