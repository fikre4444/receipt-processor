from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.endpoints import router as api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for extracting date and total from receipt images.",
    version="1.0.0"
)


app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Service is running"}