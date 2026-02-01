from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.models.receipt_db import Receipt
from app.repositories.base import BaseRepository

class ReceiptRepository(BaseRepository[Receipt]):
    def __init__(self, session: AsyncSession):
        super().__init__(Receipt, session)

    async def get_by_task_id(self, task_id: str) -> Optional[Receipt]:
        statement = select(self.model).where(self.model.task_id == task_id)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def get_history(self, limit: int = 100) -> list[Receipt]:
        statement = select(self.model).order_by(self.model.created_at.desc()).limit(limit)
        result = await self.session.execute(statement)
        return result.scalars().all()
