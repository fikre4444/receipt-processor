import os
import logging
from app.core.celery_app import celery_app
from app.services.image import ImageService
from app.services.ocr import OCRService
from app.services.parser import parse_receipt
from app.services.analysis import AnalysisService
from app.services.llm import LLMService
from app.services.storage import StorageService
from app.db import get_sync_session_context
from app.api.dependencies import get_s3_client
from app.models.receipt_db import Receipt
from pdf2image import convert_from_path

logger = logging.getLogger(__name__)

# Instantiate services
image_service = ImageService()
ocr_service = OCRService()
analysis_service = AnalysisService()
llm_service = LLMService()

@celery_app.task(bind=True)
def process_receipt_task(self, s3_key: str, generate_summary: bool):
    """
    Celery task to process receipt: 
    1. Downloads from storage
    2. OCR / Image processing
    3. Parsing & Analysis
    4. Optional LLM Summary
    5. Database Update
    """
    s3_client = get_s3_client()
    storage_service = StorageService(s3_client)
    local_temp_path = f"/tmp/{os.path.basename(s3_key)}"
    
    # Manually manage session lifecycle for Celery worker
    with get_sync_session_context() as db:
        try:
            logger.info(f"Downloading {s3_key} from storage to {local_temp_path}")
            storage_service.download_file(s3_key, local_temp_path)

            raw_text = ""
            
            if local_temp_path.lower().endswith('.pdf'):
                logger.info(f"Processing PDF: {local_temp_path}")
                pages = convert_from_path(local_temp_path, dpi=300)
                for i, page in enumerate(pages):
                    cv2_img = image_service.pil_to_cv2(page)
                    processed_img = image_service.apply_thresholding(cv2_img)
                    page_text = ocr_service.extract_text(processed_img)
                    raw_text += f"\n--- Page {i+1} ---\n{page_text}"
            else:
                logger.info(f"Processing Image: {local_temp_path}")
                with open(local_temp_path, "rb") as f:
                    file_bytes = f.read()
                processed_image = image_service.prepare_image_from_bytes(file_bytes)
                raw_text = ocr_service.extract_text(processed_image)

            parsed_data = parse_receipt(raw_text)
            audit_tags = analysis_service.analyze_receipt(parsed_data)

            summary_text = None
            if generate_summary:
                summary_text = llm_service.generate_summary(
                    raw_text, 
                    parsed_data["total"], 
                    parsed_data["date"]
                )

            # Update database record (created by API)
            receipt_record = db.query(Receipt).filter(Receipt.task_id == self.request.id).first()
            
            if receipt_record:
                receipt_record.merchant = parsed_data.get("merchant")
                receipt_record.total = parsed_data.get("total")
                receipt_record.subtotal = parsed_data.get("subtotal")
                receipt_record.tax = parsed_data.get("tax")
                receipt_record.tip = parsed_data.get("tip")
                receipt_record.discount = parsed_data.get("discount")
                receipt_record.other_fees = parsed_data.get("other_fees")
                receipt_record.date = parsed_data.get("date")
                receipt_record.summary = summary_text
                receipt_record.raw_text = raw_text
                receipt_record.tags = audit_tags
                receipt_record.status = "completed"
                
                db.commit()

            return {
                "status": "success",
                "data": {
                    "merchant": parsed_data.get("merchant"),
                    "total": parsed_data.get("total"),
                    "subtotal": parsed_data.get("subtotal"),
                    "tax": parsed_data.get("tax"),
                    "tip": parsed_data.get("tip"),
                    "discount": parsed_data.get("discount"),
                    "other_fees": parsed_data.get("other_fees"),
                    "date": parsed_data.get("date"),
                    "summary": summary_text,
                    "raw_text": raw_text,
                    "tags": audit_tags
                }
            }

        except Exception as e:
            logger.error(f"Task Failed: {e}")
            receipt_record = db.query(Receipt).filter(Receipt.task_id == self.request.id).first()
            if receipt_record:
                receipt_record.status = "error"
                db.commit()
            return {"status": "error", "error": str(e)}

        finally:
            # Clean up the temporary file on the worker
            if os.path.exists(local_temp_path):
                os.remove(local_temp_path)