import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

def prepare_image(file_bytes: bytes) -> np.ndarray:
    """
    Converts raw file bytes into a processed OpenCV image ready for OCR.
    """
    try:
        nparr = np.frombuffer(file_bytes, np.uint8)

        
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("Could not decode image. File might be corrupted.")

       
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return thresh

    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise e