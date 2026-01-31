from pydantic import BaseModel, Field
from typing import List, Optional

class LineItem(BaseModel):
    description: str
    amount: float

class ReceiptData(BaseModel):
    merchant: str = "Unknown"
    date: Optional[str] = None
    currency: str = "$"
    
    total: Optional[float] = None
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    tip: Optional[float] = None
    discount: Optional[float] = None
    
    line_items: List[LineItem] = []
    
    summary: Optional[str] = None
    raw_text: str
    tags: List[str] = []

class ReceiptResponse(BaseModel):
    status: str
    data: ReceiptData