"""
Logging utilities for ProFlow Agent.

Provides centralized logging setup with file and console handlers.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


def setup_logging(
    log_dir: str = None,
    log_level: int = logging.INFO,
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
    logger_name: str = "proflow"
) -> logging.Logger:
    """
    Set up logging with both file and console handlers.
    
    Creates logs/ directory automatically and generates timestamped log files.
    
    Args:
        log_dir: Directory for log files. Defaults to logs/ in project root.
        log_level: Overall log level (default: INFO)
        console_level: Console handler log level (default: INFO)
        file_level: File handler log level (default: DEBUG)
        logger_name: Name of the logger (default: "proflow")
    
    Returns:
        Configured logger instance
    """
    # Get or create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Determine log directory
    if log_dir is None:
        # Default to logs/ relative to project root
        project_root = Path(__file__).parent.parent.parent
        log_dir = project_root / "logs"
    else:
        log_dir = Path(log_dir)
    
    # Create logs directory if it doesn't exist
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamped log filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"proflow_{timestamp}.log"
    log_file = log_dir / log_filename
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = logging.Formatter(
        '%(levelname)-8s | %(message)s'
    )
    
    # File handler (detailed logging)
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(file_level)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    # Console handler (simpler output)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Log initial message
    logger.info(f"Logging initialized - Log file: {log_file}")
    logger.debug(f"Log levels - Console: {logging.getLevelName(console_level)}, File: {logging.getLevelName(file_level)}")
    
    return logger


def get_logger(name: str = "proflow") -> logging.Logger:
    """
    Get an existing logger instance.
    
    Args:
        name: Logger name (default: "proflow")
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Example usage
if __name__ == "__main__":
    print("Testing logger setup...")
    
    # Setup logging
    logger = setup_logging(log_level=logging.DEBUG)
    
    # Test different log levels
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")
    logger.critical("This is a CRITICAL message")
    
    # Test with exception
    try:
        raise ValueError("Test exception")
    except Exception as e:
        logger.exception("Exception occurred during test")
    
    print("\n✅ Logger test complete!")
    print(f"Check logs/ directory for proflow_*.log file")

