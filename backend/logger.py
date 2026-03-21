import logging
import sys
import os

# Force setup at project root
log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nalam_app.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(module)s:%(funcName)s:%(lineno)d - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_path, mode='a', encoding='utf-8')
    ],
    force=True  # Ensure our settings override any third-party library defaults
)

# Custom log level function for easy use
def log_info(msg):
    logging.info(msg)

def log_error(msg):
    logging.error(msg)
    
def log_warning(msg):
    logging.warning(msg)

def get_logger(name):
    return logging.getLogger(name)
