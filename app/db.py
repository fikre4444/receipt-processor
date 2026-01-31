import os
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/receipts_app")

engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# for the FastAPI Endpoints (Dependency Injection)
def get_session():
    with Session(engine) as session:
        yield session

def init_db():
    # create tables if they don't exist
    SQLModel.metadata.create_all(engine)