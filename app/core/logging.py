import logging
import sys

def setup_logging():
    """
    Configures the root logger to print to stdout.
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logging.getLogger("multipart").setLevel(logging.WARNING)