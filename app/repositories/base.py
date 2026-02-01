from typing import Generic, TypeVar, Type, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, SQLModel

ModelType = TypeVar("ModelType", bound=SQLModel)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get(self, id: Any) -> Optional[ModelType]:
        return await self.session.get(self.model, id)

    async def list(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        statement = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def create(self, obj_in: ModelType) -> ModelType:
        self.session.add(obj_in)
        await self.session.commit()
        await self.session.refresh(obj_in)
        return obj_in

    async def update(self, db_obj: ModelType, obj_in: ModelType) -> ModelType:
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            setattr(db_obj, field, obj_data[field])
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, id: Any) -> Optional[ModelType]:
        db_obj = await self.session.get(self.model, id)
        if db_obj:
            await self.session.delete(db_obj)
            await self.session.commit()
        return db_obj
