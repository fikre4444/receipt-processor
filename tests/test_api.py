import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.api.dependencies import get_receipt_repository, get_storage_service

client = TestClient(app)

# Mocked services for dependency override
class MockReceiptRepository:
    async def create(self, session, obj_in):
        return MagicMock(id=1, task_id="mock-task-id")

class MockStorageService:
    async def upload_file(self, content, filename, content_type):
        return "mock-s3-key"

# Dependency overrides
app.dependency_overrides[get_receipt_repository] = lambda: MockReceiptRepository()
app.dependency_overrides[get_storage_service] = lambda: MockStorageService()

@pytest.fixture
def mock_image_file():
    return ("test.jpg", b"fake_image_bytes", "image/jpeg")

@patch("app.api.v1.endpoints.receipts.process_receipt_task.delay")
def test_process_receipt_endpoint(mock_task_delay, mock_image_file):
    """
    Test that the POST /process-receipt endpoint correctly uploads file,
    creates DB record, and dispatches Celery task.
    """
    mock_task_delay.return_value = MagicMock(id="mock-task-id")
    
    filename, filebytes, content_type = mock_image_file
    response = client.post(
        "/api/v1/receipts/process",
        files={"file": (filename, filebytes, content_type)},
        data={"generate_summary": "true"}
    )
    
    assert response.status_code == 201
    json_data = response.json()
    assert json_data["status"] == "success"
    assert "task_id" in json_data["data"]
    
    mock_task_delay.assert_called_once()

def test_process_receipt_invalid_file_type():
    """
    Test that the API rejects non-image/non-pdf files.
    """
    response = client.post(
        "/api/v1/receipts/process",
        files={"file": ("test.txt", b"some text", "text/plain")}
    )
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]

@patch("app.api.v1.endpoints.tasks.AsyncResult")
def test_get_task_status(mock_async_result):
    """
    Test the GET /tasks/{id} endpoint.
    """
    mock_task = MagicMock()
    mock_task.state = "SUCCESS"
    mock_task.result = {"status": "success", "data": {"merchant": "Mock Shop", "total": 100.0}}
    mock_async_result.return_value = mock_task
    
    response = client.get("/api/v1/tasks/mock-task-id")
    
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "SUCCESS"
    assert json_data["result"]["data"]["merchant"] == "Mock Shop"

@patch("app.api.v1.endpoints.receipts.receipt_repo.get_multi")
async def test_get_receipt_history(mock_get_multi):
    """
    Test the GET /receipts/history endpoint.
    """
    mock_get_multi.return_value = [
        MagicMock(id=1, merchant="Shop A", total=10.0, date="2024-01-01", status="completed"),
        MagicMock(id=2, merchant="Shop B", total=20.0, date="2024-01-02", status="completed")
    ]
    
    response = client.get("/api/v1/receipts/history")
    
    assert response.status_code == 200
    json_data = response.json()
    assert len(json_data) == 2
    assert json_data[0]["merchant"] == "Shop A"