# app/logger.py
import logging
from pythonjsonlogger import json
from .config import get_settings


def get_logger(name: str = "app"):
    settings = get_settings()
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = "%(asctime)s %(levelname)s %(name)s %(message)s"
        formatter = json.JsonFormatter(fmt)  # ✅ updated import
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(settings.log_level)
    return logger
