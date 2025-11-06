# hyperx/loader/element_loader.py
"""
Element Loader
──────────────────────────────────────────────
Scans and imports all element modules in `hyperx.elements`
so their <hx:*> tags register automatically via decorators.

Designed to be safe, idempotent, and debug-friendly.
"""

import importlib
import pkgutil

from hyperx.logger.hx_logger import *

_logger = load_logger("Elements loader")
_logger.info("Elements loader initialized")


def load_elements(package: str = "hyperx.elements") -> int:
    """
    Import all modules under the given package to trigger tag registration.

    Returns:
        int: Number of successfully imported element modules.
    """
    _logger.info(f"[ElementLoader] Scanning {package} for <hx:*> components...")

    try:
        pkg = importlib.import_module(package)
    except ModuleNotFoundError:
        _logger.warning(f"[ElementLoader] Package not found: {package}")
        return 0
    except Exception as e:
        _logger.error(f"[ElementLoader] Could not import base package {package}: {e}")
        return 0

    if not hasattr(pkg, "__path__"):
        _logger.warning(f"[ElementLoader] {package} has no __path__; skipping.")
        return 0

    imported = 0
    for _, mod_name, _ in pkgutil.iter_modules(pkg.__path__):
        full_name = f"{package}.{mod_name}"
        try:
            importlib.import_module(full_name)
            _logger. debug(f"[ElementLoader] Loaded element: {full_name}")
            imported += 1
        except Exception as e:
            _logger.warning(f"[ElementLoader] Failed to import {full_name}: {e}")

    _logger.info(f"[ElementLoader] {imported} element modules imported.")
    return imported


if __name__ == "__main__":
    count = load_elements()
    _logger.info(f"[ElementLoader] ✅ Imported {count} element modules successfully.")
