"""
Logging configuration using loguru.
"""

from loguru import logger
import sys
import os
from config import settings

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Remove default loguru handler
logger.remove()

# Add handler: human-readable format to stdout
logger.add(
    sys.stdout,
    level=settings.LOG_LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} - {message}",
    colorize=True,
    enqueue=True,
    backtrace=True,
    diagnose=True,
)

# Add handler: log to file with rotation (10 MB)
logger.add(
    "logs/bot.log",
    level=settings.LOG_LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} - {message}",
    rotation="10 MB",
    retention="10 days",
    compression="zip",
    enqueue=True,
    backtrace=True,
    diagnose=True,
)

# Example of usage:
# logger.info("This is an info message")
# logger.warning("This is a warning message")
# logger.error("This is an error message")
# logger.critical("This is a critical message")