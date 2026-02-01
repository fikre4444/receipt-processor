import cv2
import numpy as np
import logging
from PIL import Image

logger = logging.getLogger(__name__)

class ImageService:
    def pil_to_cv2(self, pil_image: Image.Image) -> np.ndarray:
        """
        Converts a PIL Image (from pdf2image) to an OpenCV BGR numpy array.
        """
        return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    def apply_thresholding(self, image: np.ndarray) -> np.ndarray:
        """
        Applies Grayscale and Otsu's thresholding to a loaded OpenCV image.
        """
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            return thresh
        except Exception as e:
            logger.error(f"Error applying threshold: {e}")
            raise e

    def prepare_image_from_bytes(self, file_bytes: bytes) -> np.ndarray:
        """
        Converts raw bytes -> OpenCV Image -> Thresholded Image
        """
        image = self.decode_image(file_bytes)
        return self.apply_thresholding(image)

    def decode_image(self, file_bytes: bytes) -> np.ndarray:
        """
        Decodes raw bytes into an OpenCV image.
        """
        nparr = np.frombuffer(file_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("Could not decode image.")
        return image
