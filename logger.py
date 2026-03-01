import sys
import logging
from pythonjsonlogger import jsonlogger

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate logs if already configured
    if not logger.handlers:
        logHandler = logging.StreamHandler(sys.stdout)
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(levelname)s %(name)s %(message)s'
        )
        logHandler.setFormatter(formatter)
        logger.addHandler(logHandler)
        
    return logger

logger = setup_logger("bharatgpt")
