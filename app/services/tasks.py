import os
import logging
from app.core.celery_app import celery_app
from app.services import image_processing, ocr_engine, parser, analysis_service, llm_service
from pdf2image import convert_from_path

from app.db import SessionLocal 
from app.models.receipt_db import Receipt
from app.services.storage_service import storage_service

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def process_receipt_task(self, s3_key: str, generate_summary: bool):
    db = SessionLocal()
    local_temp_path = f"/tmp/{os.path.basename(s3_key)}"
    
    try:
        logger.info(f"Downloading {s3_key} from storage to {local_temp_path}")
        storage_service.download_file(s3_key, local_temp_path)

        raw_text = ""
        
        if local_temp_path.lower().endswith('.pdf'):
            logger.info(f"Processing PDF: {local_temp_path}")
            pages = convert_from_path(local_temp_path, dpi=300)
            for i, page in enumerate(pages):
                cv2_img = image_processing.pil_to_cv2(page)
                processed_img = image_processing.apply_thresholding(cv2_img)
                page_text = ocr_engine.extract_text_from_image(processed_img)
                raw_text += f"\n--- Page {i+1} ---\n{page_text}"
        else:
            logger.info(f"Processing Image: {local_temp_path}")
            with open(local_temp_path, "rb") as f:
                file_bytes = f.read()
            processed_image = image_processing.prepare_image_from_bytes(file_bytes)
            raw_text = ocr_engine.extract_text_from_image(processed_image)

        parsed_data = parser.parse_receipt(raw_text)
        audit_tags = analysis_service.analyze_receipt(parsed_data)

        summary_text = None
        if generate_summary:
            summary_text = llm_service.generate_receipt_summary(
                raw_text, 
                parsed_data["total"], 
                parsed_data["date"]
            )

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
                "merchant": parsed_data["merchant"],
                "total": parsed_data["total"],
                "subtotal": parsed_data["subtotal"],
                "tax": parsed_data["tax"],
                "date": parsed_data["date"],
                "discount" : parsed_data["discount"],
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
        db.close()
        # Clean up the temporary file on the worker
        if os.path.exists(local_temp_path):
            os.remove(local_temp_path)