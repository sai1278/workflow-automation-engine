import logging
from pythonjsonlogger import jsonlogger
from .config import get_settings

def get_logger(name: str = "app"):
    settings = get_settings()
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = "%(asctime)s %(levelname)s %(name)s %(message)s"
        formatter = jsonlogger.JsonFormatter(fmt)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(settings.log_level)
    return logger
