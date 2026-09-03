"""Structured logging configuration for QA-OS."""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

import structlog
from rich.logging import RichHandler

from config import settings


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    format_style: str = "json",
) -> None:
    """
    Configure structured logging with structlog and rich.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        format_style: Log format (json or text)
    """
    # Configure standard logging
    stdlib_logger = logging.getLogger()
    stdlib_logger.setLevel(log_level.upper())

    # Remove default handlers
    for handler in stdlib_logger.handlers[:]:
        stdlib_logger.removeHandler(handler)

    # Console handler with rich formatting
    console_handler = RichHandler(
        show_time=True,
        show_level=True,
        show_path=False,
        rich_tracebacks=True,
    )
    console_handler.setLevel(log_level.upper())
    stdlib_logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
        )
        file_handler.setLevel(log_level.upper())
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        stdlib_logger.addHandler(file_handler)

    # Configure structlog
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if format_style == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.extend(
            [
                structlog.processors.UnicodeDecoder(),
                structlog.dev.ConsoleRenderer(),
            ]
        )

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Structured logger instance
    """
    return structlog.get_logger(name)


# Initialize logging on import
setup_logging(
    log_level=settings.api_log_level,
    log_file="logs/qa-os.log" if not settings.debug else None,
    format_style="json" if settings.environment == "production" else "text",
)

# Get module logger
logger = get_logger(__name__)
