import pytesseract
import numpy as np
import logging
import sys

from app.core.config import settings

logger = logging.getLogger(__name__)

if settings.TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_PATH

def extract_text_from_image(image: np.ndarray) -> str:
    """
    Wraps Tesseract execution with error handling and logging.
    """
    try:
        custom_config = r'--oem 3 --psm 4'
        
        text = pytesseract.image_to_string(image, config=custom_config)
        
        if not text.strip():
            logger.warning("OCR returned empty text.")
            
        return text

    except pytesseract.TesseractNotFoundError:
        logger.critical("Tesseract is not installed or not in PATH.")
        raise RuntimeError("OCR Engine is not available.")
        
    except Exception as e:
        logger.error(f"OCR Failed: {str(e)}")
        raise RuntimeError("Failed to extract text from image.")