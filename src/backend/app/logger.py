# app/logger.py
import logging
from pythonjsonlogger import jsonlogger
from .config import get_settings

def get_logger(name: str = "app") -> logging.Logger:
    settings = get_settings()
    logger = logging.getLogger(name)

    if not logger.handlers:
        # Create a stream handler
        handler = logging.StreamHandler()
        # Define the log format
        fmt = "%(asctime)s %(levelname)s %(name)s %(message)s"
        # Use the correct JsonFormatter
        formatter = jsonlogger.JsonFormatter(fmt)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(settings.log_level)
    return logger
