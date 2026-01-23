from pydantic import BaseModel
from typing import Optional

class ReceiptData(BaseModel):
    total: Optional[float] = None
    date: Optional[str] = None
    summary: Optional[str] = None
    raw_text: str

class ReceiptResponse(BaseModel):
    status: str
    data: ReceiptData