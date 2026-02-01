# 🧾 Automated Receipt Processor

A professional, high-performance backend system for extracting and analyzing structured data from receipt images and PDFs. Built with a clean **Layered Architecture (Repository-Service Pattern)**, it leverages asynchronous task processing, OCR, and Large Language Models (LLMs) to provide deep financial insights.

---

## 🚀 Overview

This service automates the tedious task of manual receipt entry. It pre-processes images using **OpenCV**, extracts raw text via **Tesseract OCR**, and uses a sophisticated **Regex-based Financial Parser** to identify key data points (Merchant, Date, Total, Tax, etc.). Extracted records are analyzed for suspicious patterns and can be summarized using **DeepSeek/Gemma** via the OpenRouter API.

### 🏗 Architecture
The project follows a modular, layered design for maximum maintainability:
- **API Layer**: Thin controllers (FastAPI) utilizing Dependency Injection.
- **Service Layer**: Pure business logic (OCR, LLM, Storage, Image Processing).
- **Repository Layer**: Data access abstraction using SQLModel and AsyncSession.
- **Async Processing**: Distributed task queue for long-running vision/AI jobs.

---

## 🛠 Tech Stack

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.11)
- **Database**: [PostgreSQL](https://www.postgresql.org/) with [SQLModel](https://sqlmodel.tiangolo.com/) (Async)
- **Task Queue**: [Celery](https://docs.celeryq.dev/) with [RabbitMQ](https://www.rabbitmq.com/) (Broker) & [Redis](https://redis.io/) (Backend)
- **Object Storage**: [MinIO](https://min.io/) (S3-Compatible)
- **Vision/AI**: [OpenCV](https://opencv.org/), [Tesseract OCR](https://github.com/tesseract-ocr/tesseract), [OpenRouter API](https://openrouter.ai/)
- **Infrastructure**: Docker & Docker Compose
- **Frontend**: React (Vite)

---

## ✨ Key Features

1.  **Repository-Service Pattern**: Decoupled data access and business logic for better testability and clean code.
2.  **Robust OCR Pipeline**: Automated image pre-processing (Grayscale + Otsu's Thresholding) for high-accuracy extraction.
3.  **Distributed Processing**: Background tasks ensure the API remains responsive while heavy OCR and LLM jobs process in the queue.
4.  **Async/Await First**: Asynchronous database and storage operations for high concurrency.
5.  **Smart Financial Parser**: Multi-strategy extraction including labeled search and value-based fallbacks.
6.  **Expense Analysis**: Automated tagging (e.g., `HIGH_VALUE`, `WEEKEND_EXPENSE`, `FUTURE_DATE`).
7.  **Auto-Reload**: Full hot-reloading for both the API and Celery workers during development.

---

## 📂 Project Structure

```text
app/
├── api/                # API controllers & Dependency Injection
│   ├── v1/
│   │   └── endpoints/  # Split by resource (receipts, tasks)
│   └── dependencies.py # Service/Repo providers
├── core/               # Configuration, Celery app, & Logging
├── models/             # Database schemas (SQLModel)
├── repositories/       # Data access layer (CRUD)
├── services/           # Business logic (OCR, LLM, Storage, Tasks)
├── schemas/            # Pydantic DTOs
├── db.py               # Database engine & session management
└── main.py             # FastAPI entry point
```

---

## ⚙️ Development Setup

### 1. Prerequisites
- Docker & Docker Compose
- [OpenRouter API Key](https://openrouter.ai/keys) (Optional, for LLM summaries)

### 2. Configuration
Create a `.env` file in the root:
```env
DATABASE_URL=postgresql://user:password@db:5432/receipts_app
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
CELERY_RESULT_BACKEND=redis://redis:6379/0
S3_ENDPOINT=http://storage:9000
S3_KEY=minioadmin
S3_SECRET=minioadmin
OPENROUTER_API_KEY=your_key_here
```

### 3. Launching the System
```bash
# First time or when requirements.txt changes
docker compose -f docker-compose.dev.yml up --build

# Subsequent runs
docker compose -f docker-compose.dev.yml up
```

- **Frontend**: `http://localhost:5173`
- **Backend Docs**: `http://localhost:8000/docs`
- **MinIO Console**: `http://localhost:9001` (admin/minioadmin)
- **RabbitMQ Console**: `http://localhost:15672` (guest/guest)

---

## 🔄 Development Workflow

- **Hot Reload**: The system monitors files in the `app/` directory. Changes to API code will trigger a Uvicorn reload, and changes to service/task code will trigger a Celery worker restart (via `watchfiles`).
- **Database Migrations**: Tables are automatically created on startup via `init_db()`.
- **Storage**: Files are uploaded to MinIO and processed asynchronously.

---

## 🔄 CI/CD Pipeline

The project uses **GitHub Actions** located in `.github/workflows/deploy.yml`.

### Workflow Steps:
1.  **Push to Main**: Triggers the pipeline.
2.  **Backend Job**:
    *   Builds `Dockerfile.prod`.
    *   Pushes image to **Docker Hub**.
    *   Triggers **Railway** (or Render) to pull the new image and redeploy.
3.  **Frontend Job**:
    *   Installs dependencies and runs `npm run build`.
    *   Injects the live Backend URL via `VITE_API_URL`.
    *   Deploys the static `dist/` folder to **GitHub Pages**.

---

## 🧠 Architectural Decisions

### Repository-Service Pattern
I migrated from a flat service structure to a layered Repository-Service pattern.
- **Why?**: This decouples the database engine (SQLModel) from the business logic. It allows us to swap databases or mock repositories easily for testing without touching the core services.

### Asynchronous Distributed Tasks
All OCR and LLM processing is moved to **Celery**.
- **Reasoning**: Vision and AI tasks are compute-heavy and high-latency. Processing them within the FastAPI request lifecycle would cause timeouts and block other users. Celery allows the system to scale workers independently based on load.

### S3-Compatible Storage (MinIO)
I moved away from local file storage to **MinIO**.
- **Reasoning**: Local storage doesnt scale horizontally. By using an S3-compatible service, the backend becomes stateless, allowing multiple API or worker containers to share the same object store.

### Tesseract vs. EasyOCR
I chose **Tesseract** over EasyOCR for this implementation:
- **CPU Efficiency**: EasyOCR relies on PyTorch and is optimized for GPUs. For a standard CPU-based microservice, Tesseract is significantly faster and lighter.
- **Docker Image Size**: Tesseract binaries keep the image size manageable, whereas PyTorch dependencies can bloat images to >2GB.

### Tiered Regex Strategy
Receipts are unstructured, so the parser (`parser.py`) uses a tiered approach:
1.  **Contextual Search**: High-confidence matching for anchors like "Total:", "Total Amount".
2.  **Fallback Extraction**: Identifies the largest currency-formatted number as the total if labels are missing or OCR is messy.
3.  **Normalized Date Parsing**: Uses `dateparser` to safely handle varied global date formats.

---

## 🧪 Testing

```bash
# Run tests within the container
docker exec -it receipt_api_dev pytest
```

---

## 📄 License
MIT License