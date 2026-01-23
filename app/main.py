from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.endpoints import router as api_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for extracting date and total from receipt images.",
    version="1.0.0"
)

#For Cors Policy
origins = [
    "http://localhost:5173",  # Vite default port
    "http://localhost:3000",  # React default port
    "*"                       # Allow all (for development simplicity)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Service is running"}