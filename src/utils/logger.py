"""
Logging utilities for Thinking Tools MCP Server
"""
import logging
import sys
import os
from typing import Optional


def get_logger(name: str, log_file: Optional[str] = None, log_level: str = "INFO") -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (typically __name__)
        log_file: Optional log file path
        log_level: Log level (default: INFO)
    
    Returns:
        Configured logger instance
    """
    # Get log level from environment or use provided default
    level = os.getenv("MCP_LOG_LEVEL", log_level)
    log_file_path = log_file or os.getenv("MCP_LOG_FILE")
    
    logger = logging.getLogger(name)
    
    # Only add handlers if logger doesn't have any
    if not logger.handlers:
        logger.setLevel(getattr(logging, level))
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level))
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file_path:
            file_handler = logging.FileHandler(log_file_path)
            file_handler.setLevel(getattr(logging, level))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
    
    return logger
