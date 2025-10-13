#!/usr/bin/env python3
"""
update_init.py
────────────────────────────────────────────
Rebuilds hyperx/__init__.py with the correct
imports and availability flags for optional
modules (Elements, AI, Watcher, etc.).
"""

from __future__ import annotations
import os, sys, importlib, logging
from pathlib import Path
from datetime import datetime


ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
PKG_DIR = ROOT / "hyperx"
TARGET = PKG_DIR / "__init__.py"

_logger = logging.getLogger("update_init")
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

OPTIONAL_MODULES = {
    "ELEMENTS_REGISTERED": "hyperx.templatetags.hyperx_elements",
    "AI_TOOLS_AVAILABLE": "hyperx.opt.hyperx.ai_schema_autogen",
    "WATCHER_AVAILABLE": "hyperx.opt.hyperx.dataset_watch_service",
}

def module_exists(modname: str) -> bool:
    try:
        importlib.import_module(modname)
        return True
    except Exception:
        return False

def build_init():
    """Construct the text of hyperx/__init__.py"""
    version = "3.0.0"
    header = f'''"""
HyperX package initializer (auto-generated)
────────────────────────────────────────────
Updated: {datetime.now().isoformat()}
Do not edit manually; use bin/cli/generator/update_init.py
"""

from __future__ import annotations
import sys, importlib, logging
from pathlib import Path

__version__ = "{version}"
__author__ = "Faroncoder"
__email__ = "jeff.panasuik@gmail.com"
__license__ = "MIT"
__url__ = "https://github.com/faroncoder/hyperx-htmx"

from hyperx.middleware import *

'''
    # --- Elements/AI/Watcher detection ---
    status_lines = []
    for flag, modname in OPTIONAL_MODULES.items():
        available = module_exists(modname)
        status_lines.append(f'{flag} = {available}')
        if available:
            _logger.info(f"{flag} ✓  ({modname}) found")
        else:
            _logger.warning(f"{flag} ✗  ({modname}) missing")

    status_block = "\n".join(status_lines)

    # --- Logging setup ---
    logging_block = '''
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
'''

    # --- Compose final file ---
    body = f"""{header}{status_block}

{logging_block}
"""
    return body

def main():
    text = build_init()
    TARGET.write_text(text)
    _logger.info(f"✅ Updated {TARGET.relative_to(ROOT)}")

if __name__ == "__main__":
    sys.exit(main())
