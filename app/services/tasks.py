import os
import logging
from app.core.celery_app import celery_app
from app.services import image_processing, ocr_engine, parser, analysis_service, llm_service
from pdf2image import convert_from_path

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def process_receipt_task(self, file_path: str, generate_summary: bool):
    try:
        raw_text = ""
        
        # if the file is a pdf, convert each page to image and process
        if file_path.lower().endswith('.pdf'):
            logger.info(f"Processing PDF: {file_path}")
            
            # Convert PDF to list of PIL Images
            try:
                pages = convert_from_path(file_path, dpi=300)
                
                for i, page in enumerate(pages):
                    cv2_img = image_processing.pil_to_cv2(page)
                    
                    processed_img = image_processing.apply_thresholding(cv2_img)
                    
                    page_text = ocr_engine.extract_text_from_image(processed_img)
                    raw_text += f"\n--- Page {i+1} ---\n{page_text}"
                    
            except Exception as e:
                raise ValueError(f"Failed to process PDF: {str(e)}")

        else:
            logger.info(f"Processing Image: {file_path}")
            with open(file_path, "rb") as f:
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
        if os.path.exists(file_path):
            os.remove(file_path)
        return {"status": "error", "error": str(e)}