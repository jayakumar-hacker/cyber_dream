"""
logger.py
==========
Shared logging setup for CyberDreamer. Infrastructure/plumbing code, not
a model component, so it is fully implemented.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path


def get_logger(name: str, log_dir: str | Path | None = None, level: int = logging.INFO) -> logging.Logger:
    """
    Return a configured logger that writes to stdout, and optionally
    also to a rotating-free plain file under `log_dir`.

    Args:
        name: Logger name, typically `__name__` of the calling module.
        log_dir: Optional directory (e.g. `logs/<run_name>/`) to also
            write a `<name>.log` file into.
        level: Logging level, defaults to INFO.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        # Already configured (e.g. re-imported); avoid duplicate handlers.
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if log_dir is not None:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path / f"{name.replace('.', '_')}.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
