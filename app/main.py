from fastapi import FastAPI
from app.core.config import settings
from app.api.v1 import router as api_router
from fastapi.middleware.cors import CORSMiddleware
from app.core.logging import setup_logging
from app.db import init_db

setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for extracting date and total from receipt images.",
    version="1.0.0"
)

# For Cors Policy
origins = [str(origin) for origin in settings.BACKEND_CORS_ORIGINS]
if "https://*.github.io" not in origins:
    origins.append("https://*.github.io")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Service is running"}