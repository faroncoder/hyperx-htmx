#!/usr/bin/env python3
"""
bootstrap_logger.py
──────────────────────────────────────────────
Centralized logger bootstrapper for the HyperX runtime.

Provides:
  - Global log configuration
  - Colorized console output
  - Rotating file handlers
  - Single initialization guard
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from hyperx.logger.hx_logger import *


_logger = load_logger("hyperx.cmds.workers.setenv")
_logger.info("setenv initialized")



_LOGGER_BOOTSTRAPPED = False  # Guard against double init


def bootstrap_logger(level: str = None, log_dir: str = "_logs") -> None:
    """
    Bootstrap global logging configuration for HyperX.
    
    Args:
        level (str): Optional log level ("DEBUG", "INFO", etc.)
        log_dir (str): Directory for log files.
    """
    global _LOGGER_BOOTSTRAPPED
    if _LOGGER_BOOTSTRAPPED:
        return  # Avoid reconfiguring multiple times

    # ─────────────────────────────
    # 1️⃣ Resolve configuration
    # ─────────────────────────────
    env_level = os.getenv("HYPERX_DEBUG", "").lower()
    debug_mode = env_level in ("1", "true", "yes", "debug")
    log_level = level or ("DEBUG" if debug_mode else "INFO")

    log_root = Path.cwd() / log_dir
    log_root.mkdir(exist_ok=True)

    logfile = log_root / "hyperx.log"

    # ─────────────────────────────
    # 2️⃣ Define formatting
    # ─────────────────────────────
    console_fmt = "\033[92m[%(name)s]\033[0m %(levelname)s: %(message)s"
    file_fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(console_fmt))

    file_handler = RotatingFileHandler(logfile, maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(file_fmt))

    # ─────────────────────────────
    # 3️⃣ Root logger config
    # ─────────────────────────────
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        handlers=[console_handler, file_handler],
        force=True,  # override previous configs safely
    )

    # ─────────────────────────────
    # 4️⃣ Feedback to console
    # ─────────────────────────────
    logger = logging.getLogger("hyperx.bootstrap_logger")
    logger.info(f"[Bootstrap] Logging initialized at {log_level} level.")
    logger.info(f"[Bootstrap] Logs directory: {log_root}")

    _LOGGER_BOOTSTRAPPED = True
