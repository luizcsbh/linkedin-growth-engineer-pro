import logging
import os
from app.core.config import Config

def setup_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(Config.LOG_LEVEL)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    # File handler
    log_file = os.path.join('logs', f'{name}.log')
    fh = logging.FileHandler(log_file)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    
    return logger
