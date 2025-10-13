"""
HyperX package initializer (auto-generated)
────────────────────────────────────────────
Updated: 2025-10-12T23:15:35.869621
Do not edit manually; use bin/cli/generator/update_init.py
"""

from __future__ import annotations
import sys, importlib, logging
from pathlib import Path

__version__ = "3.0.0"
__author__ = "Faroncoder"
__email__ = "jeff.panasuik@gmail.com"
__license__ = "MIT"
__url__ = "https://github.com/faroncoder/hyperx-htmx"

from hyperx.middleware import *

ELEMENTS_REGISTERED = False
AI_TOOLS_AVAILABLE = False
WATCHER_AVAILABLE = False


_logger = logging.getLogger("hyperx")
if not _logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    _logger.addHandler(handler)
    _logger.setLevel(logging.INFO)

_logger.info(f"✅ HyperX {__version__} initialized")
_logger.info(f"   🧩 Elements Registered: {ELEMENTS_REGISTERED}")
_logger.info(f"   🧠 AI Tools: {AI_TOOLS_AVAILABLE}")
_logger.info(f"   👁️ Watcher: {WATCHER_AVAILABLE}")

