"""
Logging configuration and utilities for the Academic Evaluation application.
"""
import sys
from pathlib import Path
from loguru import logger
from typing import Optional

from config.settings import LOG_DIR, LOG_LEVEL, LOG_FORMAT


class AppLogger:
    """Centralized logging configuration for the application."""
    
    def __init__(self, log_level: str = LOG_LEVEL):
        """
        Initialize the application logger.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.log_level = log_level
        self.log_dir = LOG_DIR
        self.log_dir.mkdir(exist_ok=True)
        
        # Remove default logger
        logger.remove()
        
        # Configure logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Set up logging configuration with file and console handlers."""
        
        # Console handler with colors
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
            level=self.log_level,
            colorize=True
        )
        
        # File handler for all logs
        logger.add(
            self.log_dir / "app.log",
            format=LOG_FORMAT,
            level=self.log_level,
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            encoding="utf-8",
            backtrace=True,
            diagnose=True
        )
        
        # Error file handler
        logger.add(
            self.log_dir / "errors.log",
            format=LOG_FORMAT,
            level="ERROR",
            rotation="5 MB",
            retention="60 days",
            compression="zip",
            encoding="utf-8",
            backtrace=True,
            diagnose=True
        )
        
        logger.info(f"Logging initialized with level: {self.log_level}")
        logger.info(f"Log files directory: {self.log_dir}")
    
    def get_logger(self, name: Optional[str] = None):
        """Get a logger instance with optional name binding."""
        if name:
            return logger.bind(name=name)
        return logger


# Global logger instance
app_logger = AppLogger()

# Export commonly used functions
def get_logger(name: Optional[str] = None):
    """Get a logger instance."""
    return app_logger.get_logger(name)

def log_performance(operation: str, duration: float, details: dict = None):
    """Log performance metrics."""
    logger.info(f"Performance: {operation} completed in {duration:.2f} seconds")
    if details:
        logger.debug(f"  Details: {details}")

def log_user_action(action: str, user_id: str = None, details: dict = None):
    """Log user actions."""
    user_info = f"User {user_id}" if user_id else "User"
    logger.info(f"{user_info} action: {action}")
    if details:
        logger.debug(f"  Details: {details}")

def log_system_event(event: str, details: dict = None):
    """Log system events."""
    logger.info(f"System event: {event}")
    if details:
        logger.debug(f"  Details: {details}")
