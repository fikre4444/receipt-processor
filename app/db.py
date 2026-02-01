import os
from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, Session, create_engine

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/receipts_app")
# Convert to asyncpg driver if not already specified
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# ASYNC_DATABASE_URL = (
#     DATABASE_URL if "asyncpg" in DATABASE_URL else DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
# )

# Async Engine and Session
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = sessionmaker(
    bind=async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autoflush=False
)

# Sync Engine and Session (for init_db and legacy/sync tasks)
sync_engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# Dependency for FastAPI
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

# Dependency for FastAPI (Sync - used by some components if needed)
def get_session() -> Generator[Session, None, None]:
    with Session(sync_engine) as session:
        yield session

# Context Managers for manual lifecycle management (e.g. Celery tasks)
@asynccontextmanager
async def get_async_session_context() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

@contextmanager
def get_sync_session_context() -> Generator[Session, None, None]:
    with Session(sync_engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

def init_db() -> None:
    """Create tables if they don't exist. Typically run on startup."""
    SQLModel.metadata.create_all(sync_engine)
    # async with async_engine.begin() as conn:
    #     await conn.run_sync(SQLModel.metadata.create_all)