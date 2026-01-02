"""
Structured logging configuration for WeTech system
"""
import logging
import os
from pathlib import Path
from django.conf import settings

def setup_logger(name='wetech'):
    """
    Setup structured logger with file and console handlers
    
    Usage:
        from wetech.utils.logger import setup_logger
        logger = setup_logger(__name__)
        logger.info("Payment processed", extra={'invoice_id': 'INV-123'})
    """
    # Create logs directory if it doesn't exist
    log_dir = Path(settings.BASE_DIR) / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(pathname)s:%(lineno)d]',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler for all logs
    file_handler = logging.FileHandler(log_dir / 'app.log')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # File handler for errors only
    error_handler = logging.FileHandler(log_dir / 'errors.log')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.WARNING)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)
    
    return logger

# Default logger instance
logger = setup_logger()

