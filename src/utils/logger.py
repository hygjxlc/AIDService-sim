"""Logging Configuration"""
import sys
from pathlib import Path
from loguru import logger

from src.config import get_settings


def setup_logging():
    """Configure loguru logging"""
    settings = get_settings()
    
    # Remove default handler
    logger.remove()
    
    # Console handler
    logger.add(
        sys.stderr,
        level=settings.logging.level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>"
    )
    
    # File handler with rotation
    log_path = Path(settings.logging.path)
    log_path.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        log_path / "aid-service-{time:YYYY-MM-DD}.log",
        rotation="00:00",  # Daily rotation at midnight
        retention=f"{settings.logging.retention_days} days",
        level=settings.logging.level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} | {message}",
        encoding="utf-8"
    )
    
    return logger


# Named loggers for different categories
def get_access_logger():
    """Logger for access/request logs"""
    return logger.bind(category="access")


def get_business_logger():
    """Logger for business logic logs"""
    return logger.bind(category="business")


def get_error_logger():
    """Logger for error logs"""
    return logger.bind(category="error")


def get_system_logger():
    """Logger for system logs"""
    return logger.bind(category="system")
