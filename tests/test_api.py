import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)

# Use a dummy fixture for a valid image file upload
@pytest.fixture
def mock_image_file():
    return ("test.jpg", b"fake_image_bytes", "image/jpeg")

@patch("app.services.image_processing.prepare_image")
@patch("app.services.ocr_engine.extract_text_from_image")
@patch("app.services.llm_service.generate_receipt_summary")
def test_process_receipt_happy_path(mock_llm, mock_ocr, mock_img, mock_image_file):
    """
    Test the full flow with mocks.
    """
    mock_img.return_value = "processed_image_array"
    mock_ocr.return_value = "Walmart\nTotal: 50.00\nDate: 2023-01-01"
    mock_llm.return_value = "Mock AI Summary"

    filename, filebytes, content_type = mock_image_file
    response = client.post(
        "/api/v1/process-receipt",
        files={"file": (filename, filebytes, content_type)},
        data={"generate_summary": True}
    )

    assert response.status_code == 200
    json_data = response.json()
    
    assert json_data["status"] == "success"
    assert json_data["data"]["total"] == 50.00
    assert json_data["data"]["date"] == "2023-01-01"
    assert json_data["data"]["summary"] == "Mock AI Summary"

def test_process_receipt_invalid_file_type():
    """
    Test that the API rejects PDFs.
    """
    response = client.post(
        "/api/v1/process-receipt",
        files={"file": ("test.pdf", b"pdf_bytes", "application/pdf")}
    )
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]