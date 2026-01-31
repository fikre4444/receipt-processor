from sqlmodel import SQLModel, Field, JSON, Column
from typing import Optional, List
from datetime import datetime

class Receipt(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: str = Field(index=True, unique=True)
    status: str = Field(default="pending")
    
    filename: str
    s3_key: str
    
    merchant: Optional[str] = None
    date: Optional[str] = None
    total: Optional[float] = None
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    tip: Optional[float] = None
    discount: Optional[float] = None
    other_fees: Optional[float] = None
    
    summary: Optional[str] = None
    raw_text: Optional[str] = None
    tags: List[str] = Field(default=[], sa_column=Column(JSON))
    
    created_at: datetime = Field(default_factory=datetime.utcnow)