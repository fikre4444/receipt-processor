from fastapi import APIRouter, UploadFile, File, HTTPException, status, Form
import logging

from app.schemas.receipt import ReceiptResponse
from app.services import analysis_service, image_processing, ocr_engine, parser
from app.services import llm_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/process-receipt", response_model=ReceiptResponse)
async def process_receipt(file: UploadFile = File(...), generate_summary: bool = Form(False)):
    """
    Accepts an image file (JPG/PNG), extracts text using OCR, 
    and parses the Total Amount and Date.
    """
    
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Please upload a JPG or PNG image."
        )

    try:
        file_bytes = await file.read()

        processed_image = image_processing.prepare_image(file_bytes)

        raw_text = ocr_engine.extract_text_from_image(processed_image)

        extracted_total = parser.extract_total(raw_text)
        extracted_date = parser.extract_date(raw_text)

        audit_tags = analysis_service.analyze_receipt(extracted_total, extracted_date)

        summary_text = None

        if generate_summary: 
            summary_text = llm_service.generate_receipt_summary(
                raw_text=raw_text,
                total=extracted_total,
                date=extracted_date
            )
        else:
            logger.info("Skipping AI summary generation (user opted out).")

        return {
            "status": "success",
            "data": {
                "total": extracted_total,
                "date": extracted_date,
                "summary": summary_text,
                "raw_text": raw_text,
                "tags": audit_tags
            }
        }

    except ValueError as e:
        logger.error(f"Input Error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
        
    except RuntimeError as e:
        logger.error(f"System Error: {e}")
        raise HTTPException(status_code=500, detail="OCR Engine failure.")
        
    except Exception as e:
        logger.error(f"Unexpected Error: {e}")
        raise HTTPException(status_code=500, detail="Internal processing error.")