"""Structured logging configuration"""
import logging
import logging.config

from .config import LOG_LEVEL


def setup_logging() -> None:
    """Configure application-wide structured logging."""
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                },
            },
            "loggers": {
                "app": {
                    "handlers": ["console"],
                    "level": LOG_LEVEL,
                    "propagate": False,
                },
                "uvicorn.error": {
                    "level": LOG_LEVEL,
                },
                "uvicorn.access": {
                    "level": LOG_LEVEL,
                },
            },
            "root": {
                "handlers": ["console"],
                "level": LOG_LEVEL,
            },
        }
    )


logger = logging.getLogger(__name__)
