"""Structured logging setup for backend services."""

import logging
import sys

import structlog


def configure_logging(level: int = logging.INFO) -> None:
    """Configure standard and structured logging processors."""
    logging.basicConfig(level=level, format="%(message)s", stream=sys.stdout)
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

