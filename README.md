# Automated Receipt Processor

A robust, full-stack internal tool designed to extract structured data (Total Amount, Date, Vendor) from receipt images. It features an automated **Date and Category Analysis** engine and an optional **GenAI** layer for contextual summarization.

## 🚀 Project Overview

This service accepts image uploads (JPG/PNG), pre-processes them using OpenCV, extracts text via Tesseract OCR, and applies a multi-strategy Regex parser. It provides immediate visual feedback via a React frontend and returns actionable analysis tags (e.g., "High Value", "Future Date").

## 🛠 Tech Stack

*   **Backend:** FastAPI (Python 3.11), Uvicorn
*   **Core Logic:** OpenCV (Image Processing), Tesseract (OCR), Regex (Parsing), Pydantic (Validation)
*   **Frontend:** React, Vite, Standard CSS
*   **AI/LLM:** OpenRouter API (DeepSeek/Gemma)
*   **Infrastructure:** Docker, Docker Compose (Dev & Prod), Nginx
*   **CI/CD:** GitHub Actions (Automated Build & Deploy)
*   **Testing:** Pytest, HTTPX

## ✨ Key Features

1.  **Robust OCR Pipeline:** Uses Grayscale and Otsu's Thresholding to handle noisy images.
2.  **Smart Parsing Logic:**
    *   **Total/Date:** Prioritizes context labels ("Total:", "Date:") with regex fallbacks.
    *   **Analysis Service:** Automatically flags receipts (e.g., `HIGH_VALUE`, `OLD_RECEIPT`, `MISSING_DATA`) using business logic defined in `analysis_service.py`.
3.  **Opt-in AI Analysis:** Users can enable LLM analysis to categorize expenses and summarize items. *Default is False to prioritize low latency.*
4.  **Production Architecture:** Multi-stage Docker builds using Nginx for the frontend and optimized Python images for the backend.
5.  **CI/CD Pipeline:** Fully automated deployment to Docker Hub, Railway/Render (Backend), and GitHub Pages (Frontend).

---

## 📂 Project Structure

```text
receipt-processor/
├── .github/workflows/      # CI/CD Configuration
│   └── deploy.yml          # GitHub Actions Pipeline
├── app/
│   ├── api/                # API Route Controllers
│   ├── core/               # Configuration & Logging
│   ├── schemas/            # Pydantic Models
│   ├── services/
│   │   ├── analysis_service.py # Analysis Logic
│   │   ├── image_processing.py # OpenCV Logic
│   │   ├── llm_service.py      # OpenRouter/LLM Integration
│   │   ├── ocr_engine.py       # Tesseract Wrapper
│   │   └── parser.py           # Regex Extraction Logic
│   └── main.py             # App Entry Point
├── frontend-react/
│   ├── src/                # React Components
│   ├── Dockerfile.dev      # Node.js Dev Server
│   └── Dockerfile.prod     # Nginx Static Server (Multi-stage)
├── tests/                  # Unit & Integration Tests
├── Dockerfile.dev          # Backend Dev (Hot Reload)
├── Dockerfile.prod         # Backend Prod (Optimized)
├── docker-compose.dev.yml  # Local Development Orchestration
├── docker-compose.prod.yml # Local Production Simulation
└── requirements.txt        # Python Dependencies
```

---

## ⚙️ Prerequisites

*   **Docker** & **Docker Compose**
*   **Git**
*   *For Deployment:* Docker Hub Account, Railway/Render Account.

---

## 🚀 Running Locally

This provides two distinct environments for running the application locally.

### 1. Development Mode (Hot Reload)
*Best for coding. Changes to files update the app instantly.*

1.  **Configure Environment:**
    Create a `.env` file in the root:
    ```env
    OPENROUTER_API_KEY=your_key_here
    OPENROUTER_MODEL=google/gemma-2-27b-it:free
    ```

2.  **Run with Docker Compose:**
    ```bash
    docker-compose -f docker-compose.dev.yml up --build
    ```

3.  **Access:**
    *   Frontend: `http://localhost:5173`
    *   Backend Docs: `http://localhost:8000/docs`

### 2. Production Simulation
*Best for testing the final build artifact (Nginx + Uvicorn) before deployment.*

This uses `Dockerfile.prod` files. The frontend is compiled to static HTML and served via Nginx on Port 80. The backend runs without hot-reload.

1.  **Run Production Compose:**
    ```bash
    docker-compose -f docker-compose.prod.yml up --build
    ```

2.  **Access:**
    *   Frontend: `http://localhost` (Standard HTTP Port 80)
    *   Backend: Internal container network on Port 8000.

---

## 🔄 CI/CD Pipeline

The project uses **GitHub Actions** located in `.github/workflows/deploy.yml`.

### Workflow Steps:
1.  **Push to Main:** Triggers the pipeline.
2.  **Backend Job:**
    *   Builds `Dockerfile.prod`.
    *   Pushes image to **Docker Hub**.
    *   Triggers **Railway** (or Render) to pull the new image and redeploy.
3.  **Frontend Job:**
    *   Installs dependencies and runs `npm run build`.
    *   Injects the live Backend URL via `VITE_API_URL`.
    *   Deploys the static `dist/` folder to **GitHub Pages**.

### Required GitHub Secrets:
To activate this, add the following to Repository Settings > Secrets:
*   `DOCKERHUB_USERNAME` / `DOCKERHUB_PASSWORD`
*   `RAILWAY_TOKEN` (or Deploy Hook URL)
*   `VITE_API_URL` (The live URL of your deployed backend, e.g., `https://api.your-app.com`)

---

## 🧠 Architectural Decisions

### Why Tesseract vs. EasyOCR?
I chose **Tesseract** over EasyOCR for this implementation:
*   **CPU Efficiency:** EasyOCR relies on PyTorch and is optimized for GPUs. For a standard CPU-based microservice, Tesseract is significantly faster and lighter.
*   **Docker Image Size:** Tesseract binaries keep the image size manageable, whereas PyTorch dependencies can bloat images to >2GB.

### The Regex Strategy
Receipts are unstructured. Our parser (`parser.py`) uses a tiered strategy:
1.  **Contextual Search:** Looks for specific anchors like "Total:", "Amount Due".
2.  **Fallback:** If anchors are missing, it scans for the largest currency-formatted number.
3.  **Date Parsing:** Uses `dateparser` to normalize formats like "Oct 15, 2023" or "10/15/23" into ISO 8601.

### LLM Integration (Opt-In)
I integrated Generative AI via OpenRouter to categorize expenses.
*   **Reasoning:** This feature is **False by default**. LLM calls introduce network latency (1-3s). I prioritize the instant OCR response and allow the user to "Enable AI Analysis" only when they need deeper insights.

---

## 🧪 Testing

### Running Tests in Docker
The most accurate way to test (ensures Tesseract is present):

```bash
# Run all tests
docker exec -it receipt_api_dev pytest

# Run specific integration tests
docker exec -it receipt_api_dev pytest tests/test_api.py
```

### Running Tests Locally without docker (not preferred)
Requires `tesseract` installed on your host machine.

```bash
pip install -r requirements.txt
pytest
```

---

## 📄 License

MIT License