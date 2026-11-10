"""Configure rotating application logs."""

from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler

from src.app.config import load_config


def setup_logging(level: int | str | None = None) -> logging.Logger:
    """Configure the application logger with a 2 MiB rotating log file."""
    config = load_config()
    selected_level = level or os.environ.get("SMART_VACUUM_LOG_LEVEL", "INFO")
    if isinstance(selected_level, str):
        selected_level = selected_level.upper()
    logger = logging.getLogger("smart_vacuum")
    logger.setLevel(selected_level)
    logger.propagate = False
    if not any(getattr(handler, "_smart_vacuum", False) for handler in logger.handlers):
        handler = RotatingFileHandler(
            config.logs_dir / "application.log",
            maxBytes=2 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8",
        )
        handler._smart_vacuum = True  # type: ignore[attr-defined]
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        logger.addHandler(handler)
    return logger
